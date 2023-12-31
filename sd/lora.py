import asyncio
import base64
import json
import os
import shutil
import uuid
from os import path

import requests
import websockets
from loguru import logger
from sd import biz
from codec import parser


def gen_lora(
    files: list[str],
    style: int,
    tags: list[str],
    use_default_tag=True,
    resolution="512,512",
) -> list[dict[str, str]]:
    model_name = biz.get_model_name(style)
    logger.info(f"Dealing {files} with model {model_name}, using tags: {tags}")
    mq = parser.Parser()
    gen = []
    train_dir = str(uuid.uuid4())
    os.mkdir(path.join("lora-scripts", "train", train_dir))
    os.mkdir(path.join("lora-scripts", "train", train_dir, "unprocessed"))
    for file in files:
        shutil.move(
            file,
            path.join(
                "lora-scripts", "train", train_dir, "unprocessed", file.split("/")[-1]
            ),
        )
    if use_default_tag:
        get_pics_tags_save_in_dir(
            resolution,
            os.path.abspath(
                path.join(
                    "lora-scripts",
                    "train",
                    train_dir,
                    "unprocessed",
                )
            ),
            os.path.abspath(
                path.join(
                    "lora-scripts",
                    "train",
                    train_dir,
                    str(mq.get_lora_train_num()) + "_" + "pics",
                )
            ),
        )

    async def get_ws_info(model, train_data_name):
        async with websockets.connect(
            mq.get_lora_scripts_ws_addr() + "/train/network",
            ping_interval=100000,
            ping_timeout=100000,
        ) as ws:
            await ws.send(
                json.dumps(
                    {
                        "model": model,
                        "is_v2_model": False,
                        "train_data": train_data_name,
                        "resolution": "512,512",  # TODO 这个地方以后需要支持自定义的 resolution
                    }
                )
            )
            logger.info("Starting to wait for remote ws return")
            msg = await ws.recv()
            data = json.loads(msg)
            if str(data["status"]) != "1001":
                logger.error("status error")
                return
            logger.info("Task is running now")
            models_gen = []
            try:
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if data["status"] == 2001:
                        models_gen.append(
                            {"model_name": data["model_name"], "loss": data["loss"]}
                        )
                        logger.info(
                            "A lora generated, with model name: "
                            + data["model_name"]
                            + ", with loss: "
                            + str(data["loss"])
                        )
                    if data["status"] == 2002:
                        logger.info(
                            "Epoch finished once, num: "
                            + str(data["epoch"])
                            + ", loss: "
                            + str(data["loss"])
                            + ", step: "
                            + str(data["step"])
                        )
                    if data["status"] == 3001:
                        logger.info("Finished task, msg: " + data["message"])
                        break
            except websockets.ConnectionClosed as e:
                logger.error(
                    f"WS Connection with lora scripts server was closed by the remote! Exception: {e}"
                )
            except Exception as e:
                logger.error(
                    f"WS Connection with lora scripts server has a Exception: {e}"
                )
            # While End
            sorted_gen = sorted(
                models_gen, key=lambda sp: abs(sp["loss"] - mq.get_loss_decided_num())
            )
            for lora in sorted_gen[:4]:
                name = str(uuid.uuid4())
                target_dir = path.join(
                    "stable-diffusion-webui", "models", "Lora", name + ".safetensors"
                )
                shutil.move(
                    path.join("lora-scripts", "output", lora["model_name"]),
                    target_dir,
                )
                gen.append(
                    {
                        "preview": gen_preview_pic(name, resolution),
                        "token": name,
                    }
                )
                logger.info(
                    "Selected lora with loss: "
                    + str(lora["loss"])
                    + ", model name: "
                    + name
                )

    asyncio.get_event_loop().run_until_complete(get_ws_info(model_name, train_dir))
    return gen


def gen_pic(
    lora_model_name: str,
    prompt: str,
    resolution: str = "512,512",
    lora_strength: str = "1",
    checkpoint: str = "chilloutmix",
) -> list[str]:
    (width, height) = resolution.split(",")
    mq = parser.Parser()
    gen = []
    for _ in range(4):
        response = requests.post(
            mq.get_sd_service_addr() + "/sdapi/v1/txt2img",
            # TODO 这个地方可以添加多 Lora 融合机制
            data=json.dumps(
                {
                    "denoising_strength": 0,
                    "prompt": f"<lora:{lora_model_name}:{lora_strength}>," + prompt,
                    "used_checkpoint_model": checkpoint,
                    "negative_prompt": "",
                    "seed": -1,
                    "batch_size": 1,
                    "n_iter": 1,
                    "steps": mq.get_sd_generate_steps(),
                    "cfg_scale": 7,
                    "width": int(width),
                    "height": int(height),
                    "restore_faces": False,
                    "tiling": False,
                    "override_settings": {
                        "sd_model_checkpoint": "chilloutmix.safetensors [fc2511737a]"
                    },
                    "sampler_index": "DPM++ 2M Karras",
                }
            ),
        )
        gen.append(generate_file(response.json()["images"][0]))
    return gen


def generate_file(b64c: str) -> str:
    img_data = base64.b64decode(b64c)
    file = path.join("generate", str(uuid.uuid4()) + ".png")
    with open(file, "wb") as f:
        f.write(img_data)
    return file


def gen_preview_pic(lora_model_name: str, resolution: str) -> str:
    (width, height) = resolution.split(",")
    mq = parser.Parser()
    logger.info("use lora: " + lora_model_name + "to generate preview picture.")
    response = requests.post(
        mq.get_sd_service_addr() + "/sdapi/v1/txt2img",
        data=json.dumps(
            {
                "denoising_strength": 0,
                "prompt": f"<lora:{lora_model_name}:1>",
                "used_checkpoint_model": "chilloutmix",
                "negative_prompt": "",
                "seed": -1,
                "batch_size": 1,
                "n_iter": 1,
                "steps": mq.get_sd_generate_steps(),
                "cfg_scale": 7,
                "width": int(width),
                "height": int(height),
                "restore_faces": False,
                "tiling": False,
                "override_settings": {
                    "sd_model_checkpoint": "chilloutmix.safetensors [fc2511737a]"
                },
                "sampler_index": "DPM++ 2M Karras",
            }
        ),
    )
    return generate_file(response.json()["images"][0])


def get_pics_tags_save_in_dir(resolution: str, train_dir: str, output_dir: str) -> bool:
    (width, height) = resolution.split(",")
    mq = parser.Parser()
    response = requests.post(
        mq.get_sd_service_addr() + "/sdapi/v1/preprocess",
        data=json.dumps(
            {
                "process_src": train_dir,
                "process_dst": output_dir,
                "process_width": int(width),
                "process_height": int(height),
                "process_caption_deepbooru": True,
                "process_keep_original_size": False,
                "process_flip": False,
                "process_split": True,
                "id_task": str(uuid.uuid4()),
                "preprocess_txt_action": "ignore",
                "process_caption": False,
            }
        ),
        headers={"Content-Type": "application/json;charset=utf-8"},
    )
    if response.json()["info"] != "preprocess complete":
        logger.warning(
            "Error occur when saving pic's tags, train_dir: "
            + train_dir
            + ", output_dir: "
            + output_dir
            + ", error: "
            + response.json()["info"]
        )
        return False
    return True

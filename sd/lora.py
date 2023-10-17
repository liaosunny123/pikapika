import uuid
from os import path
from loguru import logger

from sd import biz


def gen_lora(files: list[str], style: int, tags: list[str]) -> list[dict[str, str]]:
    model_name = biz.get_model_name(style)
    logger.info(f"Dealing {files} with model {model_name}, using tags: {tags}")
    # TODO: 补充生成 Lora 模型的逻辑
    gen = []
    for file in files:
        gen.append(
            {
                "preview": path.join("generate", "default.png"),
                "token": str(uuid.uuid4()),
            }
        )
    return gen


def gen_pic(lora_model_path: str, prompt: str) -> list[str]:
    # TODO: 处理图片
    return ["generate/default.png"]

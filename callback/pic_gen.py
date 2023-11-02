import json
import uuid
from time import sleep

import requests
from loguru import logger

from codec import parser
from sd import lora
from storage import oss
import traceback


def callback(ch, method, properties, body):
    data = json.loads(body)
    mq = parser.Parser()
    i = 1  # CallBack 逻辑，使得重试次数分时
    while i <= 3:
        try:
            logger.info("Get Task and run gen picture task.")
            gen = lora.gen_pic(data["lora"], data["prompt"])
            logger.info("Generated images from OSS.")
            logger.info("Oss upload event by taskId: " + str(data["taskId"]))
            response = requests.post(
                data["callback"],
                data=json.dumps(
                    {
                        "ret": 0,
                        "msg": f"OK!",
                        "pictures": oss.upload_target_files(
                            mq.get_oss_access_key_id(),
                            mq.get_oss_access_key_secret(),
                            data["oss"]["endPoint"],
                            data["oss"]["bucketName"],
                            gen,
                            mq.get_upload_prefix(),
                        ),
                        "taskId": data["taskId"],
                        "loraId": data["lora"],
                    }
                ),
                headers={"Content-Type": "application/json;charset=utf-8"},
            )
            logger.info("Uploaded images to OSS.")
            if response.status_code != 200:
                logger.error(
                    f'Http request meet trouble, can not connect with remote server: {data["callback"]}, status code: {response.status_code}'
                )
            else:
                logger.info("End request!")
                break
        except Exception as e:
            if "callback" in data and data["callback"][:4] == "http":
                trace = uuid.uuid4()
                traceback.print_exc()
                logger.error(
                    f"Pikapika meets a trouble when dealing pic-gen, error: {e}, trace-id: {trace}"
                )
                response = requests.post(
                    data["callback"],
                    data=json.dumps(
                        {
                            "ret": "403",
                            "msg": f"服务器遇到内部错误，请联系管理员查看，Trace Id 为：{trace}",
                            "loraId": data["lora"],
                            "taskId": data["taskId"],
                            "pictures": [],
                        }
                    ),
                    headers={"Content-Type": "application/json;charset=utf-8"},
                )
                if response.status_code != 200:
                    logger.error(
                        f'Http request meet trouble, can not connect with remote server: {data["callback"]}'
                    )
                i = i + 1
                sleep(10 * i * 1000)
            i = 4
            logger.error(f"Meet error content for {data}")
            traceback.print_exc()

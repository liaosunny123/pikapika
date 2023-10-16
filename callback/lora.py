import json
import uuid
from time import sleep

import requests
from loguru import logger

from codec import parser
from sd import lora
from storage import oss


def callback(ch, method, properties, body):
    data = json.loads(body)
    mq = parser.Parser()
    i = 1  # Callback 重试逻辑
    while i <= 3:
        try:
            img_list = oss.download_target_files(
                mq.get_oss_access_key_id(),
                mq.get_oss_access_key_secret(),
                data["oss"]["endPoint"],
                data["oss"]["bucketName"],
                list[str](data["oss"]["filePath"]),
            )
            logger.info("Got source images from OSS. ")
            gens = lora.gen_lora(img_list, data["style"], list[str](data["tags"]))
            logger.info("Generated images from OSS.")
            rets = oss.upload_target_files(
                mq.get_oss_access_key_id(),
                mq.get_oss_access_key_secret(),
                data["oss"]["endPoint"],
                data["oss"]["bucketName"],
                gens,
                mq.get_upload_prefix(),
            )
            logger.info("Uploaded images to OSS.")
            response = requests.post(
                data["callback"], data={"ret": "0", "msg": f"OK!", "lora": rets}
            )
            if response.status_code != 200:
                logger.error(
                    f'Http request meet trouble , can not connect with remote server: {data["callback"]}'
                )
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            if "callback" in data and data["callback"][:4] == "http":
                trace = uuid.uuid4()
                logger.error(
                    f"Pikapika meets a trouble when dealing lora, error: {e}, trace-id: {trace}"
                )
                response = requests.post(
                    data["callback"],
                    data={
                        "ret": "403",
                        "msg": f"服务器遇到内部错误，请联系管理员查看，Trace Id 为：{trace}",
                        "lora": [],
                    },
                )
                if response.status_code != 200:
                    logger.error(
                        f'Http request meet trouble, can not connect with remote server: {data["callback"]}'
                    )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                i = i + 1
                sleep(10 * i * 1000)
            i = 4
            logger.error(f'Meet error content for {data}, Exception: {e}')
            ch.basic_ack(delivery_tag=method.delivery_tag)

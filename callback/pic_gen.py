import json
import uuid

import requests

from loguru import logger
from sd import lora
from storage import oss
from codec import parser


def callback(ch, method, properties, body):
    data = json.loads(body)
    mq = parser.Parser()
    try:
        gen = lora.gen_pic(data['lora'], data['prompt'])
        response = requests.post(data['callback'], data={
            'ret': '0',
            'msg': f'OK!',
            'pictures': oss.upload_target_files(mq.get_oss_access_key_id(),
                                                mq.get_oss_access_key_secret(),
                                                data['oss']['endPoint'],
                                                data['oss']['bucketName'],
                                                gen,
                                                mq.get_upload_prefix())
        })
        if response.status_code != 200:
            logger.error(f'Http request meet trouble, can not connect with remote server: {data["callback"]}')
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        trace = uuid.uuid4()
        logger.error(f'Pikapika meets a trouble when dealing pic-gen, error: {e}, trace-id: {trace}')
        response = requests.post(data['callback'], data={
            'ret': '403',
            'msg': f'服务器遇到内部错误，请联系管理员查看，Trace Id 为：{trace}',
            'pictures': []
        })
        if response.status_code != 200:
            logger.error(f'Http request meet trouble, can not connect with remote server: {data["callback"]}')
        ch.basic_ack(delivery_tag=method.delivery_tag)

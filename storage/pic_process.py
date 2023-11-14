import uuid

import requests

from codec import parser
from alibabacloud_imageseg20191230.client import Client
from alibabacloud_imageseg20191230.models import SegmentCommodityAdvanceRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.models import RuntimeOptions
from loguru import logger
from os import path
from PIL import Image


def seg_pic(file_path: list[str]) -> list[str]:
    mq = parser.Parser()
    config = Config(
        access_key_id=mq.get_oss_access_key_id(),
        access_key_secret=mq.get_oss_access_key_secret(),
        endpoint=mq.get_seg_pics_endpoint(),
        region_id=mq.get_seg_pics_region_id(),
    )
    client = Client(config)
    gen = []
    for file in file_path:
        img = open(file, "rb")
        seg_req = SegmentCommodityAdvanceRequest()
        seg_req.image_urlobject = img
        runtime_opt = RuntimeOptions()
        try:
            resp = client.segment_commodity_advance(seg_req, runtime_opt)
            temp_file_name = str(uuid.uuid4()) + ".jpg"
            file_name = str(uuid.uuid4()) + ".png"
            with Image.open(requests.get(resp.body.data.image_url).content) as img:
                white_bg = Image.new("RGBA", img.size, "WHITE")
                white_bg.paste(img, (0, 0), img)
                non_transparent = white_bg.convert("RGB")
                non_transparent.save(path.join("generate", file_name), "PNG")
            gen.append(path.join("generate", file_name))
            logger.info(f"generate white background picture: {file_name}")
        except Exception as e:
            logger.warning(f"Error occurs when segmenting pictures, Exception: {e}")
    return gen

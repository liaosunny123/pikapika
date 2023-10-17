import uuid
from os import path

import oss2
from oss2 import Auth
from loguru import logger


def download_target_files(
    access_key_id: str,
    access_key_secret: str,
    end_point: str,
    bucket_name: str,
    file_path: list[str],
) -> list[str]:
    auth = oss2.ProviderAuth(Auth(access_key_id, access_key_secret))
    bucket = oss2.Bucket(auth.credentials_provider, end_point, bucket_name)
    ret = []
    for file in file_path:
        local_file = str(uuid.uuid4())
        bucket.get_object_to_file(file, path.join(".", "download", local_file))
        logger.info(f"Got file from OSS with key: {file}, target at {local_file}")
        ret.append(path.join("download", str(uuid.uuid4())))
    return ret


def upload_target_files(
    access_key_id: str,
    access_key_secret: str,
    end_point: str,
    bucket_name: str,
    file_path: list[str],
    upload_prefix: str,
) -> list[str]:
    auth = oss2.ProviderAuth(Auth(access_key_id, access_key_secret))
    bucket = oss2.Bucket(auth.credentials_provider, end_point, bucket_name)
    ret = []
    for file in file_path:
        local_file = str(uuid.uuid4())
        bucket.put_object_from_file(f"{upload_prefix}/{local_file}.jpg", file)
        logger.info(f"Got file from OSS with key: {file}, target at {local_file}")
        ret.append(f"download/{uuid.uuid4()}")
    return ret


def upload_target_file(
    access_key_id: str,
    access_key_secret: str,
    end_point: str,
    bucket_name: str,
    file_path: str,
    upload_prefix: str,
) -> str:
    auth = oss2.ProviderAuth(Auth(access_key_id, access_key_secret))
    bucket = oss2.Bucket(auth.credentials_provider, end_point, bucket_name)
    ret = ""
    local_file = str(uuid.uuid4())
    bucket.put_object_from_file(f"{upload_prefix}/{local_file}.jpg", file_path)
    logger.info(f"Got file from OSS with key: {file_path}, target at {local_file}")
    ret = f"{upload_prefix}/{local_file}.jpg"
    return ret

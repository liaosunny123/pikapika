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
        ret.append(path.join("download", local_file))
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
        remote_file = str(uuid.uuid4())
        logger.info(
            f"Uploaded Oss files, with file path: {file}, remote file: {remote_file}"
        )
        bucket.put_object_from_file(f"{upload_prefix}/{remote_file}.jpg", file)
        ret.append(f"{upload_prefix}/{remote_file}.jpg")
    return ret


def upload_target_file(
    access_key_id: str,
    access_key_secret: str,
    end_point: str,
    bucket_name: str,
    file_path: str,
    upload_prefix: str,
) -> str:
    logger.info(f"Uploaded Oss file, with file path: {file_path}")
    auth = oss2.ProviderAuth(Auth(access_key_id, access_key_secret))
    bucket = oss2.Bucket(auth.credentials_provider, end_point, bucket_name)
    ret = ""
    remote_file = str(uuid.uuid4())
    bucket.put_object_from_file(f"{upload_prefix}/{remote_file}.jpg", file_path)
    logger.info(
        f"Uploaded Oss file, with remote key: {upload_prefix}/{remote_file}.jpg, local file: {file_path}"
    )
    ret = f"{upload_prefix}/{remote_file}.jpg"
    return ret

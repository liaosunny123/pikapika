import uuid

import oss2
from oss2.credentials import StaticCredentialsProvider


def download_target_files(
    access_key_id: str,
    access_key_secret: str,
    end_point: str,
    bucket_name: str,
    file_path: list[str],
) -> list[str]:
    auth = oss2.ProviderAuth(
        StaticCredentialsProvider(access_key_id, access_key_secret)
    )
    bucket = oss2.Bucket(auth.credentials_provider, end_point, bucket_name)
    ret = []
    for file in file_path:
        bucket.get_object_to_file(file, f"download/{uuid.uuid4()}")
        ret.append(f"download/{uuid.uuid4()}")
    return ret


def upload_target_files(
    access_key_id: str,
    access_key_secret: str,
    end_point: str,
    bucket_name: str,
    file_path: list[str],
    upload_prefix: str,
) -> list[str]:
    auth = oss2.ProviderAuth(
        StaticCredentialsProvider(access_key_id, access_key_secret)
    )
    bucket = oss2.Bucket(auth.credentials_provider, end_point, bucket_name)
    ret = []
    for file in file_path:
        bucket.put_object_from_file(f"{upload_prefix}/{uuid.uuid4()}.jpg", file)
        ret.append(f"download/{uuid.uuid4()}")
    return ret

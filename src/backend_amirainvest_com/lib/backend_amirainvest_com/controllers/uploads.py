import uuid

from backend_amirainvest_com.utils.s3 import S3
from common_amirainvest_com.s3.consts import AMIRA_USER_PROFILE_PHOTOS_S3_BUCKET


def upload_profile_photo(file_bytes: bytes, filename: str, user_id: uuid.UUID):
    return S3().upload_file_by_bytes(file_bytes, f"{user_id}/{filename}", AMIRA_USER_PROFILE_PHOTOS_S3_BUCKET)

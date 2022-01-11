from backend_amirainvest_com.utils.s3 import S3
from common_amirainvest_com.s3.consts import AMIRA_USER_PROFILE_PHOTOS_S3_BUCKET, AMIRA_POST_PHOTOS_S3_BUCKET


def upload_profile_photo(file_bytes: str, user_id: str, filename: str):
    return S3().upload_file_by_bytes(file_bytes, f"{user_id}/{filename}", AMIRA_USER_PROFILE_PHOTOS_S3_BUCKET)


def upload_post_photo(file_bytes: str, filename: str, user_id: str, post_id: int):
    return S3().upload_file_by_bytes(file_bytes, f"{user_id}/{post_id}/{filename}", AMIRA_POST_PHOTOS_S3_BUCKET)

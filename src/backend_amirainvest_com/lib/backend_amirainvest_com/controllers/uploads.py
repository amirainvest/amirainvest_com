from backend_amirainvest_com.utils.s3 import S3
from common_amirainvest_com.s3.consts import AMIRA_USER_PROFILE_PHOTOS_S3_BUCKET


def upload_profile_photo(file_bytes: bytes, filename: str, user_id: str):
    s3 = S3()
    key = f"{user_id}/{filename}"
    return_url = s3.upload_file_by_bytes(file_bytes, key, AMIRA_USER_PROFILE_PHOTOS_S3_BUCKET)
    s3.set_object_acl("public-read", AMIRA_USER_PROFILE_PHOTOS_S3_BUCKET, key)
    return return_url

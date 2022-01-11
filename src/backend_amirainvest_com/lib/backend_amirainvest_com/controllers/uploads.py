from backend_amirainvest_com.utils.s3 import S3


def upload_profile_photo(user_id: str, filepath: str):
    # TODO: UPDATE TO PULL S3 FROM CONFIG FILE & SET VIA ENVIRONMENT VARIABLE
    return S3().upload_file(filepath, "prod-temp-amira-user-profile-photos", f"{user_id}/{filepath}")


def upload_post_photo(filepath: str, user_id: str, post_id: int):
    # TODO: UPDATE TO PULL S3 FROM CONFIG FILE & SET VIA ENVIRONMENT VARIABLE
    return S3().upload_file(filepath, "prod-temp-amira-post-photos", f"{user_id}/{post_id}/{filepath}")

from backend_amirainvest_com.utils.s3_utils import S3


def upload_profile_photo(filepath):
    # TODO: SET UP S3 FILEPATH
    # TODO: UPLOAD DIFFERENT SIZES, GET SPECIFICATIONS FROM FRONTEND
    return S3().upload_file(filepath, "amira-user-profile-photos", filepath)

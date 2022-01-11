import os
from datetime import datetime

from fastapi import APIRouter, File, Security, UploadFile

from backend_amirainvest_com.controllers import uploads, users
from backend_amirainvest_com.controllers.auth import auth_dep
from backend_amirainvest_com.models.user import UserCreate, UserUpdate
from common_amirainvest_com.schemas.schema import UsersModel


router = APIRouter(prefix="/user", tags=["User"], dependencies=[Security(auth_dep, scopes=[])])


@router.get("", status_code=200, response_model=UsersModel)
async def get_user(user_id: str):
    return (await users.get_user(user_id)).__dict__


@router.put("", status_code=200, response_model=UsersModel)
async def update_user(user_id: str, user_data: UserUpdate):
    return (await users.update_user(user_id=user_id, user_data=user_data.dict(exclude_none=True)))._asdict()


# TODO: ALL WORKING OTHER THAN BOTO3 CRED ERROR
@router.post("", status_code=200, response_model=UsersModel)
async def create_user(user_data: UserCreate):
    return (await users.handle_user_create(user_data.dict())).__dict__


@router.get("/is_existing", status_code=200)
async def get_is_existing_user(user_id: str):
    return True if (await users.get_user(user_id)) else False


@router.put("/deactivate", status_code=200, response_model=UsersModel)
async def deactivate_user(user_id: str):
    return (await users.update_user(user_id, {"is_deactivated": True}))._asdict()


@router.put("/reactivate", status_code=200, response_model=UsersModel)
async def reactivate_user(user_id: str):
    return (await users.update_user(user_id, {"is_deactivated": False}))._asdict()


@router.put("/mark_deleted", status_code=200, response_model=UsersModel)
async def delete_user(user_id: str):
    return (await users.update_user(user_id, {"is_deleted": True, "deleted_at": datetime.utcnow()}))._asdict()


@router.put("/unmark_deleted", status_code=200, response_model=UsersModel)
async def undelete_user(user_id: str):
    return (await users.update_user(user_id, {"is_deleted": False, "deleted_at": None}))._asdict()


# TODO: ALL WORKING OTHER THAN BOTO3 CRED ERROR
@router.post("/upload_profile_picture", status_code=200, response_model=UsersModel)
async def upload_profile_picture(user_id: str, image: UploadFile = File(...)):
    # TODO: ADD VALIDATION & SIZING AS REQUESTED BY FRONTEND
    with open(image.filename, "wb+") as file:
        file.write(image.file.read())
    s3_file_url = uploads.upload_profile_photo(image.filename)
    os.remove(image.filename)  # TODO do this in a temp file in memory

    return (await users.update_user(user_id, {"picture_url": s3_file_url}))._asdict()


@router.put("/claim_user/", status_code=200, response_model=UsersModel)
async def claim_user(user_id: str):
    # WHAT DO WE NEED TO DO HERE?
    # SHOULD WE JUST DELETE THE OLD USER & HAVE THEM SIGN UP?
    # MAYBE REMAP THEIR SUBSCRIBERS TO THEIR NEW USER_ID?
    return (await users.update_user(user_id, {"is_claimed": True}))._asdict()

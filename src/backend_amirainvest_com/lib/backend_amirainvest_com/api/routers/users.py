import os
from datetime import datetime

from fastapi import APIRouter, File, Security, UploadFile

from backend_amirainvest_com.controllers import uploads, users
from backend_amirainvest_com.controllers.auth import auth_dep
from backend_amirainvest_com.models.user import UserCreate
from common_amirainvest_com.schemas.schema import UsersModel


router = APIRouter(prefix="/user", tags=["User"], dependencies=[Security(auth_dep, scopes=[])])


@router.get("", status_code=200, response_model=UsersModel)
async def get_user(user_id: str):
    user = await users.get_user(user_id)
    return user.__dict__


@router.put("", status_code=200, response_model=UsersModel)
async def update_user(user: UsersModel):
    user = await users.update_user(user.dict())  # type: ignore # TODO fix
    return user


@router.post("", status_code=200, response_model=UsersModel)
async def create_user(user_data: UserCreate):
    user = await users.handle_user_create(user_data.dict())
    return user


@router.get("/is_existing", status_code=200)
async def get_is_existing_user(user_id: str):
    user: dict = await users.get_user(user_id)
    return {"existing": True if user else False}


@router.put("/deactivate", status_code=200, response_model=UsersModel)
async def deactivate_user(user_id: str):
    user = await users.get_user(user_id)
    user.is_deactivated = True
    return (await users.update_user(user.__dict__)).__dict__


@router.put("/reactivate", status_code=200, response_model=UsersModel)
async def reactivate_user(user_id: str):
    user = await users.get_user(user_id)
    user.is_deactivated = False
    return (await users.update_user(user.__dict__)).__dict__


@router.put("/mark_deleted", status_code=200, response_model=UsersModel)
async def delete_user(user_id: str):
    user = await users.get_user(user_id)
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    return (await users.update_user(user.__dict__)).__dict__


@router.put("/unmark_deleted", status_code=200, response_model=UsersModel)
async def undelete_user(user_id: str):
    user = await users.get_user(user_id)
    user.is_deleted = False
    user.deleted_at = None
    return (await users.update_user(user.__dict__)).__dict__


@router.post("/upload_profile_picture", status_code=200, response_model=UsersModel)
async def upload_profile_picture(user_id: str, image: UploadFile = File(...)):
    s3_file_url = uploads.upload_profile_photo(image.file.read(), image.filename, user_id)
    user = await users.get_user(user_id)
    user.picture_url = s3_file_url
    return (await users.update_user(user.__dict__)).__dict__


@router.put("/claim_user", status_code=200, response_model=UsersModel)
async def claim_user(user_id: str):
    user = await users.get_user(user_id)
    user.is_claimed = True
    return (await users.update_user(user)).__dict__

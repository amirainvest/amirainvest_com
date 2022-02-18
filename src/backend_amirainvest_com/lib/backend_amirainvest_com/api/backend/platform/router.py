from typing import List
from fastapi import APIRouter, Depends, File, status, UploadFile

from backend_amirainvest_com.platform.model import PlatformModel, CreatePlatformModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id



router = APIRouter(prefix="/platforms", tags=["Platform Users/Claims"])


@router.post(
    "/get", status_code=status.HTTP_200_OK, response_model=List[PlatformModel], response_model_exclude_none=True
)
async def get_platforms_route(token=Depends(auth_depends_user_id)):
    return await get_controller(user_id=token["https://amirainvest.com/user_id"])


@router.post(
    "/create", status_code=status.HTTP_200_OK, response_model=List[CreatePlatformModel], response_model_exclude_none=True
)
async def create_platforms_route(platform_data: t.List[PlatformModel], token=Depends(auth_depends_user_id)):
    claimed_platforms, unclaimed_platforms = await check_platforms(platform_data)
    if len(claimed_platforms)> 0:
        #response code 425 return t.List[PlatformModel]. User can't claim. Contact us if in error
        pass
    elif len(unclaimed_platforms)>0:
        #response code 427 return t.List[PlatformModel]  User can choose to claim
        pass
    else:
        user_id=token["https://amirainvest.com/user_id"]
        return await create_platforms(user_id, platform_data)



@router.post(
    "/claim", status_code=status.HTTP_200_OK, response_model='TBD', response_model_exclude_none=True
)
async def claim_platforms_route():
    #update husk info
    #update subscribers, posts
    #generate notifications
    pass



@router.post(
    "/update", status_code=status.HTTP_200_OK, response_model='TBD', response_model_exclude_none=True
)
async def update_platforms_route():
    #have an is_deleted field here
    #will need to check for collisions here too. FE will need to reverify
    pass


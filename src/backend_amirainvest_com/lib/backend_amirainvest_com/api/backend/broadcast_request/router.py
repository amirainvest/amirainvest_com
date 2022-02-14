from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.broadcast_request.controller import create_controller, get_controller
from backend_amirainvest_com.api.backend.broadcast_request.model import GetModel, ListModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(
    prefix="/broadcast_request",
    tags=["Broadcast Request"],
)


@router.post("/list", status_code=status.HTTP_200_OK, response_model=ListModel)
async def list_route(creator_id: str, token=Depends(auth_depends_user_id)):
    broadcast_request = await get_controller(creator_id)
    broadcast_request_data = [x.dict() for x in broadcast_request]
    return {"results": broadcast_request_data, "result_count": len(broadcast_request_data)}


@router.post("/create", status_code=status.HTTP_200_OK, response_model=GetModel)
async def create_route(creator_id: str, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    broadcast_request = await create_controller(user_id, creator_id)
    broadcast_request = broadcast_request.dict()
    return broadcast_request

from fastapi import APIRouter, Security, status

from backend_amirainvest_com.api.backend.broadcast_request.controller import create_controller, get_controller
from backend_amirainvest_com.api.backend.broadcast_request.model import GetModel, ListModel
from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(
    prefix="/broadcast_request",
    tags=["Broadcast Request"],
    dependencies=[Security(auth_dep, scopes=[])],
)


@router.post("/list", status_code=status.HTTP_200_OK, response_model=ListModel)
async def list_route(creator_id: str):
    broadcast_request = await get_controller(creator_id)
    broadcast_request_data = [x.dict() for x in broadcast_request]
    return {"results": broadcast_request_data, "result_count": len(broadcast_request_data)}


@router.post("/create", status_code=status.HTTP_200_OK, response_model=GetModel)
async def create_route(user_id: str, creator_id: str):
    broadcast_request = await create_controller(user_id, creator_id)
    broadcast_request = broadcast_request.dict()
    return broadcast_request

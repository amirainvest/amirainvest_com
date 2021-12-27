from typing import List

from fastapi import APIRouter, Security

from backend_amirainvest_com.controllers import broadcast_requests
from backend_amirainvest_com.controllers.auth import auth_dep
from common_amirainvest_com.schemas.schema import BroadcastRequestsModel


router = APIRouter(
    prefix="/broadcast_requests", tags=["Broadcast Requests"], dependencies=[Security(auth_dep, scopes=[])],
)


@router.get("/", status_code=200, response_model=List[BroadcastRequestsModel])
async def get_broadcast_requests_for_creator(creator_id: str):
    broadcast_request = await broadcast_requests.get_broadcast_requests_for_creator(creator_id)
    broadcast_request_data = [x.__dict__ for x in broadcast_request]
    return broadcast_request_data


@router.post("/", status_code=200, response_model=BroadcastRequestsModel)
async def create_broadcast_request(requester_id: str, creator_id: str):
    broadcast_request = await broadcast_requests.create_broadcast_request(requester_id, creator_id)
    broadcast_request = broadcast_request.__dict__
    return broadcast_request

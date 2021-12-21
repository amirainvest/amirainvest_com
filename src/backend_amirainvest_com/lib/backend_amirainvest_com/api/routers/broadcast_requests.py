from typing import List

from fastapi import APIRouter, Depends, Response

from backend_amirainvest_com.controllers import broadcast_requests
from backend_amirainvest_com.controllers.auth import auth_required, token_auth_scheme


router = APIRouter(prefix="/broadcast_requests", tags=["Broadcast Requests"])


@router.get("/", status_code=200, response_model=List[broadcast_requests.broadcast_requests_pydantic_model])
@auth_required
async def get_broadcast_requests_for_creator(
    creator_id: str, response: Response, token: str = Depends(token_auth_scheme)
):
    broadcast_request = await broadcast_requests.get_broadcast_requests_for_creator(creator_id)
    broadcast_request_data = [x.__dict__ for x in broadcast_request]
    return broadcast_request_data


@router.post("/", status_code=200, response_model=broadcast_requests.broadcast_requests_pydantic_model)
@auth_required
async def create_broadcast_request(
    requester_id: str, creator_id: str, response: Response, token: str = Depends(token_auth_scheme)
):
    broadcast_request = await broadcast_requests.create_broadcast_request(requester_id, creator_id)
    broadcast_request = broadcast_request.__dict__
    return broadcast_request

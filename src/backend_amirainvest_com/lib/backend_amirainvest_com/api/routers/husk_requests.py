from typing import List

from fastapi import APIRouter, Security

from backend_amirainvest_com.controllers import husk_requests
from backend_amirainvest_com.controllers.auth import auth_dep
from backend_amirainvest_com.models.husk_request import CreateHuskRequestModel
from common_amirainvest_com.schemas.schema import HuskRequestsModel


router = APIRouter(prefix="/husk_requests", tags=["Husk Requests"], dependencies=[Security(auth_dep, scopes=[])])


@router.get("", status_code=200, response_model=List[HuskRequestsModel])
async def get_husk_requests():
    husk_request = await husk_requests.get_husk_requests()
    husk_request_data = [x.__dict__ for x in husk_request]
    return husk_request_data


@router.post("", status_code=201, response_model=HuskRequestsModel)
async def create_husk_request(
    husk_request_data: CreateHuskRequestModel,
):
    husk_request = await husk_requests.create_husk_request(husk_request_data.dict())
    husk_request = husk_request.__dict__
    return husk_request


@router.delete("", status_code=200)
async def delete_husk_request(husk_request_id: int):
    await husk_requests.delete_husk_request(husk_request_id)
    return 200

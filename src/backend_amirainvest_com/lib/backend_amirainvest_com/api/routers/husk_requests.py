from typing import List

from fastapi import APIRouter, Depends

from backend_amirainvest_com.controllers import husk_requests
from backend_amirainvest_com.controllers.auth import auth_required, token_auth_scheme


router = APIRouter(prefix="/husk_requests", tags=["Husk Requests"])


@router.get("/", status_code=200, response_model=List[husk_requests.husk_requests_pydantic_model])
@auth_required
async def get_husk_requests(token: str = Depends(token_auth_scheme)):
    husk_request = await husk_requests.get_husk_requests()
    husk_request_data = [x.__dict__ for x in husk_request]
    print(husk_request_data)
    return husk_request_data


@router.post("/", status_code=201, response_model=husk_requests.husk_requests_pydantic_model)
@auth_required
async def create_husk_request(
    husk_request_data: husk_requests.husk_requests_pydantic_model,
    token: str = Depends(token_auth_scheme),
):
    husk_request = await husk_requests.create_husk_request(husk_request_data.dict())
    husk_request = husk_request.__dict__
    return husk_request


@router.delete("/", status_code=200)
@auth_required
async def delete_husk_request(husk_request_id: int, token: str = Depends(token_auth_scheme)):
    await husk_requests.delete_husk_request(husk_request_id)
    return 200

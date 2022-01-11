from fastapi import APIRouter

from backend_amirainvest_com.controllers.application import config


router = APIRouter(prefix="/application", tags=["Application"])


@router.get("/config", status_code=200)
async def get_application_config():
    return config

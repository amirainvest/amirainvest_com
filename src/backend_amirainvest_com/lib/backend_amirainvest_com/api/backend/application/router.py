from fastapi import APIRouter, status

from backend_amirainvest_com.api.backend.application.controller import get_config


router = APIRouter(prefix="/application", tags=["Application"])


@router.get("/config", status_code=status.HTTP_200_OK)
async def config_route():
    return await get_config()

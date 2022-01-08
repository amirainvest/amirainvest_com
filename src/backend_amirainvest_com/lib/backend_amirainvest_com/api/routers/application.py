from fastapi import APIRouter, Security

from backend_amirainvest_com.controllers.application import config


# from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(
    prefix="/application",
    tags=["Application"],
    # dependencies=[Security(auth_dep, scopes=[])]
)


@router.get("/config", status_code=200)
async def get_application_config():
    return config

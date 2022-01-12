from fastapi import APIRouter, Security

from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("", dependencies=[Security(auth_dep, scopes=[])])
async def root():
    return [{"message": "Welcome to the API Homepage"}]


@router.get("/health_check")
def health_check():
    return [{"message": "API healthy. Hello World!!"}]

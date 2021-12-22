from fastapi import APIRouter, Depends

from backend_amirainvest_com.controllers.auth import auth_required, token_auth_scheme


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/")
@auth_required
async def root(token: str = Depends(token_auth_scheme)):
    return [{"message": "Welcome to the API Homepage"}]


@router.get("/health_check")
def health_check():
    return [{"message": "API healthy. Hello World!!"}]

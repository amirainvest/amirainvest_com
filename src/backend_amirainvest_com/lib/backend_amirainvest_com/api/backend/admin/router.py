from fastapi import APIRouter, status


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/health_check", status_code=status.HTTP_200_OK)
def health_check_route():
    return status.HTTP_200_OK

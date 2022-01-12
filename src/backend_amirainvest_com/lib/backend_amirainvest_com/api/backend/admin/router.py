from fastapi import APIRouter


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/health_check")
def health_check_route():
    return [{"message": "API healthy. Hello World!!"}]

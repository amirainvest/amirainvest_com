from fastapi import APIRouter


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/")
def root():
    return [{"message": "Welcome to the API Homepage"}]


@router.get("/health_check")
def health_check():
    return [{"message": "API healthy. Hello World!!"}]

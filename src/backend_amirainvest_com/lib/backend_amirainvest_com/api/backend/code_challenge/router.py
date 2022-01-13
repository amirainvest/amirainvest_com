from fastapi import APIRouter

from backend_amirainvest_com.api.backend.code_challenge.controller import CodeChallenge


router = APIRouter(prefix="/code_challenge", tags=["Code Challenge"])


@router.get("", status_code=200)
async def get_route():
    challenge = CodeChallenge()
    return {"verify": challenge.verify, "challenge": challenge.challenge}

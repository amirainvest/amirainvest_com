from fastapi import APIRouter

from backend_amirainvest_com.controllers import code_challenge


router = APIRouter(prefix="/code_challenge", tags=["Code Challenge"])


@router.get("/", status_code=201)
async def get_code_challenge():
    challenge = code_challenge.CodeChallenge()
    return {"verify": challenge.verify, "challenge": challenge.challenge}

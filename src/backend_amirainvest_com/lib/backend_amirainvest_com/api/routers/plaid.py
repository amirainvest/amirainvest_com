from fastapi import APIRouter, Security
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(prefix='/plaid', tags=["Feed"], dependencies=[Security(auth_dep, scopes=[])])

@router.get("/link", status_code=200, response_class=HTMLResponse)
async def get_link(user_id: str):


# @router.post('/link', status_code=200)

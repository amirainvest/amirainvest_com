from fastapi import APIRouter, Depends, status
from backend_amirainvest_com.controllers.auth import auth_depends_user_id
from backend_amirainvest_com.api.backend.company_route.model import CompanyResponse
from backend_amirainvest_com.api.backend.company_route.controller import get_security_info, toggle_company_on
from decimal import Decimal


router = APIRouter(prefix="/company", tags=['Company'])


# TODO Will the ticker_symbol be passed in via a route/query param/body?
@router.post('/company', status_code=status.HTTP_200_OK, response_model=CompanyResponse)
async def get_company_info_route(ticker_symbol: str):
    security = await get_security_info(ticker_symbol)

    # Start collecting real-time pricing
    if not security.collect:
        await toggle_company_on(security.id)

    return CompanyResponse(
        name="",
        ticker="",
        industry="",
        asset_type="",
        founding_date="",
        description="",
        week_high_52=Decimal(),
        week_low_52=Decimal(),
        open=Decimal(),
        close=Decimal(),
        market_cap=Decimal(),
        average_volume=Decimal()
    )

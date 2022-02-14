from fastapi import APIRouter, status

from backend_amirainvest_com.api.backend.company_route.controller import (
    get_company_breakdown,
    get_minute_pricing,
    get_security_info,
)
from backend_amirainvest_com.api.backend.company_route.model import CompanyResponse, IntradayPricing
from backend_amirainvest_com.controllers.auth import auth_depends, Depends


router = APIRouter(prefix="/company", tags=["Company"])


# TODO Will the ticker_symbol be passed in via a route/query param/body?
@router.post("/company", status_code=status.HTTP_200_OK, response_model=CompanyResponse)
async def get_company_info_route(ticker_symbol: str, token=Depends(auth_depends)):
    return get_company_breakdown(ticker_symbol=ticker_symbol)


@router.post("/intraday", status_code=status.HTTP_200_OK, response_model=IntradayPricing)
async def get_intraday_pricing(ticker_symbol: str, token=Depends(auth_depends)):
    security = await get_security_info(ticker_symbol=ticker_symbol)
    intraday_pricing = await get_minute_pricing(security_id=security.id)
    return IntradayPricing(prices=intraday_pricing)

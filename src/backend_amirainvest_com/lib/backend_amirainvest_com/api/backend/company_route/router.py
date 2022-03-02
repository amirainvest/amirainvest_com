from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.company_route.controller import (
    get_company_breakdown,
    get_five_day_pricing,
    get_intraday_pricing,
    get_listed_companies,
)
from backend_amirainvest_com.api.backend.company_route.model import (
    CompanyRequest,
    CompanyResponse,
    ListedCompany,
    PricingResponse,
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/company", tags=["Company"])


# TODO Will the ticker_symbol be passed in via a route/query param/body?
@router.post("", status_code=status.HTTP_200_OK, response_model=CompanyResponse)
async def get_company_info_route(company_info_req: CompanyRequest, token=Depends(auth_depends_user_id)):
    return await get_company_breakdown(ticker_symbol=company_info_req.ticker_symbol)


@router.post("/intraday", status_code=status.HTTP_200_OK, response_model=PricingResponse)
async def get_intraday_pricing_route(intraday_req: CompanyRequest, token=Depends(auth_depends_user_id)):
    intraday_pricing = await get_intraday_pricing(ticker_symbol=intraday_req.ticker_symbol)
    return PricingResponse(prices=intraday_pricing)


@router.post("/week", status_code=status.HTTP_200_OK, response_model=PricingResponse)
async def get_five_day_pricing_route(five_day_req: CompanyRequest, token=Depends(auth_depends_user_id)):
    five_day_pricing = await get_five_day_pricing(ticker_symbol=five_day_req.ticker_symbol)
    return PricingResponse(prices=five_day_pricing)


@router.post("/list", status_code=status.HTTP_200_OK, response_model=list[ListedCompany])
async def get_listed_companies_route(token=Depends(auth_depends_user_id)):
    listed_companies = await get_listed_companies()
    return listed_companies

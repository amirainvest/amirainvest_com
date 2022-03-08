from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.portfolio.controller import (
    get_portfolio_holdings,
    get_portfolio_summary,
    get_portfolio_trades,
)
from backend_amirainvest_com.api.backend.portfolio.model import (
    HoldingsRequest,
    HoldingsResponse,
    PortfolioRequest,
    PortfolioResponse,
    PortfolioSummaryRequest,
    TradingHistoryResponse,
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/summary", status_code=status.HTTP_200_OK, response_model=PortfolioResponse)
async def route_get_portfolio_summary(portfolio_request: PortfolioSummaryRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return await get_portfolio_summary(
        user_id=user_id,
        creator_id=portfolio_request.user_id,
        start_date=portfolio_request.start_date,
        end_date=portfolio_request.end_date,
    )


@router.post("/holdings", status_code=status.HTTP_200_OK, response_model=HoldingsResponse)
async def route_get_portfolio_holdings(holdings_request: HoldingsRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return await get_portfolio_holdings(user_id=user_id, creator_id=holdings_request.user_id)


@router.post("/trades", status_code=status.HTTP_200_OK, response_model=TradingHistoryResponse)
async def route_get_portfolio_trades(portfolio_request: PortfolioRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return await get_portfolio_trades(
        user_id=user_id,
        creator_id=portfolio_request.user_id,
        symbols=portfolio_request.symbols,
        last_date=portfolio_request.last_trade_date,
        limit=portfolio_request.limit,
    )

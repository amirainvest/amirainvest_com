from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.portfolio.controller import (
    get_portfolio_holdings,
    get_portfolio_summary,
    get_portfolio_trades,
    get_user_subscription,
)
from backend_amirainvest_com.api.backend.portfolio.model import (
    HoldingsResponse,
    PortfolioRequest,
    PortfolioResponse,
    PortfolioSummaryRequest,
    PortfolioType,
    TradingHistoryResponse,
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/summary", status_code=status.HTTP_200_OK, response_model=PortfolioResponse)
async def route_get_portfolio_summary(portfolio_request: PortfolioSummaryRequest, token=Depends(auth_depends_user_id)):
    # user_id = token["https://amirainvest.com/user_id"]
    # requesting_creator = await is_requesting_creator(user_id=user_id, requesting_user_id=portfolio_request.user_id)
    return await get_portfolio_summary(
        user_id=portfolio_request.user_id,
        is_creator=False,
        start_date=portfolio_request.start_date,
        end_date=portfolio_request.end_date,
    )


@router.post("/holdings", status_code=status.HTTP_200_OK, response_model=HoldingsResponse, responses={})
async def route_get_portfolio_holdings(portfolio_request: PortfolioRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    requesting_creator = await is_requesting_creator(user_id=user_id, requesting_user_id=portfolio_request.user_id)
    portfolio_holdings = await get_portfolio_holdings(user_id=user_id, is_creator=requesting_creator)
    return HoldingsResponse(
        portfolio_type=PortfolioType.Creator if requesting_creator else PortfolioType.User, holdings=portfolio_holdings
    )


@router.post("/trades", status_code=status.HTTP_200_OK, response_model=TradingHistoryResponse)
async def route_get_portfolio_trades(portfolio_request: PortfolioRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    requesting_creator = await is_requesting_creator(user_id=user_id, requesting_user_id=portfolio_request.user_id)
    portfolio_trades = await get_portfolio_trades(user_id=user_id, is_creator=requesting_creator)
    return TradingHistoryResponse(
        portfolio_type=PortfolioType.Creator if requesting_creator else PortfolioType.User, trades=portfolio_trades
    )


async def is_requesting_creator(user_id: str, requesting_user_id: str) -> bool:
    requesting_creator = False
    if user_id != user_id:
        subscriber = await get_user_subscription(user_id=user_id, creator_id=requesting_user_id)
        if subscriber is None:
            raise Exception("user is not a subscriber of the creator")
        requesting_creator = True
    return requesting_creator

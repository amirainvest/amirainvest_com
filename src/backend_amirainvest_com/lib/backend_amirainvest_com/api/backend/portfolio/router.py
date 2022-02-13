from decimal import Decimal

from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.portfolio.controller import (
    get_user_subscription,
    get_portfolio_holdings,
    get_portfolio_trades,
)
from backend_amirainvest_com.api.backend.portfolio.model import (
    HoldingsResponse,
    Portfolio,
    PortfolioRequest,
    PortfolioType,
    TradingHistoryResponse,
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/summary", status_code=status.HTTP_200_OK)
async def route_get_portfolio_summary(portfolio_request: PortfolioRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    requesting_creator = await is_requesting_creator(user_id=user_id, requesting_user_id=portfolio_request.user_id)

    return Portfolio(
        id=portfolio_request.user_id,
        return_history=[],
        benchmark_return_history=[],
        portfolio_allocation=[],
        total_return=Decimal(0),
        beta=Decimal(0),
        sharpe_ratio=Decimal(0),
        percentage_long=Decimal(0),
        percentage_short=Decimal(0),
        percentage_gross=Decimal(0),
        percentage_net=Decimal(0),
        portfolio_type=PortfolioType.Creator if requesting_creator else PortfolioType.User,
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
            raise Exception("user is not a subscriber of creator")
        requesting_creator = True
    return requesting_creator

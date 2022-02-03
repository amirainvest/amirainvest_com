import uuid

from arrow import Arrow
from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.portfolio.controller import (
    get_buy_date,
    get_holdings,
    get_portfolio_value,
    get_ticker_symbol_by_plaid_id,
)
from backend_amirainvest_com.api.backend.portfolio.model import Holding
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/summary", status_code=status.HTTP_200_OK)
async def get_summary(user_id: uuid.UUID, token=Depends(auth_depends_user_id)):
    pass


@router.post("/holdings", status_code=status.HTTP_200_OK, response_model=list[Holding], responses={})
async def route_get_holdings(user_id: uuid.UUID, token=Depends(auth_depends_user_id)):
    response = []
    holdings = await get_holdings(user_id=user_id)
    portfolio = await get_portfolio_value(user_id=user_id)
    for cur_holding in holdings:
        security = await get_ticker_symbol_by_plaid_id(cur_holding.security_id)
        buy_date = await get_buy_date(user_id, security.security_id, cur_holding.quantity)

        market_value = cur_holding.ticker_price * cur_holding.quantity
        response.append(
            Holding(
                ticker=security.ticker,
                ticker_price=cur_holding.ticker_price,
                ticker_price_time=Arrow.fromdatetime(cur_holding.ticker_price_time),
                percentage_of_portfolio=market_value / portfolio.value,
                buy_date=buy_date,
                market_value=market_value,
            )
        )
    return response


@router.post("/trading-history", status_code=status.HTTP_200_OK)
async def get_trading_history(user_id: uuid.UUID, token=Depends(auth_depends_user_id)):
    pass

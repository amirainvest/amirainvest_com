from decimal import Decimal
import uuid

from arrow import Arrow

from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile

from backend_amirainvest_com.controllers.auth import auth_depends, auth_depends_user_id
from backend_amirainvest_com.api.backend.portfolio.controller import (
    get_holdings, get_recent_stock_price,
    get_ticker_symbol_by_plaid_id,
)
from backend_amirainvest_com.api.backend.portfolio.model import Holding


router = APIRouter(prefix="/portfolio", tags=['Portfolio'])


@router.post('/summary', status_code=status.HTTP_200_OK)
async def get_summary(user_id: uuid.UUID, token=Depends(auth_depends_user_id)):
    pass


@router.post('/holdings', status_code=status.HTTP_200_OK, response_model=list[Holding], responses={})
async def route_get_holdings(user_id: uuid.UUID, token=Depends(auth_depends_user_id)):
    response = []
    holdings = await get_holdings(user_id=user_id)
    # portfolio = await get_portfolio_value(user_id=user_id)
    for plaid_holding in holdings:
        ticker = await get_ticker_symbol_by_plaid_id(plaid_holding.security_id)
        iex_security = await get_recent_stock_price(ticker_symbol=ticker)
        # buy_date = await get_buy_date(user_id, holding.ticker_symbol)
        response_holding = Holding(
            ticker=plaid_holding.ticker,
            ticker_price=plaid_holding.ticker_price,
            ticker_price_time=Arrow.fromdatetime(plaid_holding.ticker_price_time),
            percentage_of_portfolio=None,
            buy_date=None,
            market_value=plaid_holding.ticker_price * plaid_holding.quantity
        )
        if iex_security is not None:
            market_value = Decimal(iex_security.price * plaid_holding.quantity)
            response_holding.ticker_price = iex_security.price
            response_holding.ticker_price_time = Arrow.fromdatetime(iex_security.price_time)
            # response_holding.percentage_of_portfolio = Decimal(market_value/portfolio_value)
            # response_holding.buy_date = buy_date
            response_holding.market_value = market_value
        response.append(response_holding)
    return response


@router.post('/trading-history', status_code=status.HTTP_200_OK)
async def get_trading_history(user_id: uuid.UUID, token=Depends(auth_depends_user_id)):
    pass

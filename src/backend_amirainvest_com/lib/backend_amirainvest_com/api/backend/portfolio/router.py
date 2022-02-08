from decimal import Decimal

from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.portfolio.controller import get_buy_date, get_holdings, get_trading_history
from backend_amirainvest_com.api.backend.portfolio.model import (
    HistoricalTrade,
    Holding,
    HoldingsResponse,
    PortfolioType,
    PortfolioValue,
    TradingHistoryResponse,
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/summary", status_code=status.HTTP_200_OK)
async def get_summary(user_id: str, token=Depends(auth_depends_user_id)):
    pass


@router.post("/holdings", status_code=status.HTTP_200_OK, response_model=HoldingsResponse, responses={})
async def route_get_holdings(user_id: str, token=Depends(auth_depends_user_id)):
    holdings = await get_holdings(user_id=user_id)
    portfolio = get_portfolio_value(holdings=holdings, user_id=user_id)

    holdings_res = []
    for holding in holdings:
        fa = holding.FinancialAccountCurrentHoldings
        ps = holding.PlaidSecurities

        # TODO Move this to brokerage data -- create another column called "original_buy_date" or something
        buy_date = await get_buy_date(user_id=user_id, security_id=ps.id, position_quantity=fa.quantity)

        market_value = fa.latest_price * fa.quantity
        holdings_res.append(
            Holding(
                ticker=ps.ticker_symbol,
                ticker_price=fa.latest_price,
                ticker_price_time=fa.latest_price_date,
                percentage_of_portfolio=market_value / portfolio.value,
                buy_date=buy_date,
                market_value=market_value,
            )
        )
    return HoldingsResponse(portfolio_type=PortfolioType.User, holdings=holdings_res)  # TODO how to get user or creator


@router.post("/trading-history", status_code=status.HTTP_200_OK, response_model=TradingHistoryResponse)
async def route_get_trading_history(user_id: str, token=Depends(auth_depends_user_id)):
    # Get list of trades
    trade_history = await get_trading_history()

    trades_res_list = []
    percentage_change_in_pos = Decimal(100)
    for trade in trade_history:
        fat = trade.FinancialAccountTransactions

        trades_res_list.append(
            HistoricalTrade(
                trade_date=fat.posting_date,
                ticker=trade.PlaidSecurities.ticker_symbol,
                transaction_type=fat.type,
                transaction_price=fat.price,
                transaction_market_value=fat.price * fat.quantity,
                percentage_change_in_position=percentage_change_in_pos,
            )
        )

    return TradingHistoryResponse(portfolio_type=PortfolioType.User, trades=trades_res_list)


def get_portfolio_value(holdings: list, user_id: str) -> PortfolioValue:
    portfolio_value = PortfolioValue(user_id=user_id, value=0)
    for holding in holdings:
        fa = holding.FinancialAccountCurrentHoldings
        value = portfolio_value.value + Decimal(fa.quantity * fa.latest_price)
        portfolio_value.value = value

    return portfolio_value

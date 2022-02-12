from decimal import Decimal

from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.portfolio.controller import (
    get_buy_date,
    get_holdings,
    get_trading_history,
    get_user_subscription,
)
from backend_amirainvest_com.api.backend.portfolio.model import (
    HistoricalTrade,
    Holding,
    HoldingsResponse,
    Portfolio,
    PortfolioRequest,
    PortfolioType,
    PortfolioValue,
    TradingHistoryResponse,
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/summary", status_code=status.HTTP_200_OK)
async def get_summary(portfolio_request: PortfolioRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    requesting_creator = False
    if user_id != portfolio_request.user_id:
        subscriber = await get_user_subscription(user_id=user_id, creator_id=portfolio_request.user_id)
        if subscriber is None:
            raise Exception("user is not a subscriber of creator")
        requesting_creator = True

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
async def route_get_holdings(portfolio_request: PortfolioRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    requesting_creator = False
    if user_id != portfolio_request.user_id:
        subscriber = await get_user_subscription(user_id=user_id, creator_id=portfolio_request.user_id)
        if subscriber is None:
            raise Exception("user is not a subscriber of creator")
        requesting_creator = True

    holdings = await get_holdings(user_id=portfolio_request.user_id)
    portfolio = get_portfolio_value(holdings=holdings, user_id=portfolio_request.user_id)

    holdings_res = []
    for holding in holdings:
        fa = holding.FinancialAccountCurrentHoldings
        ps = holding.PlaidSecurities

        # TODO Move this to brokerage data -- create another column called "original_buy_date" or something
        # TODO Review...
        buy_date = await get_buy_date(
            user_id=portfolio_request.user_id, security_id=ps.id, position_quantity=fa.quantity
        )

        market_value = fa.latest_price * fa.quantity
        holdings_res.append(
            Holding(
                ticker=ps.ticker_symbol,
                ticker_price=fa.latest_price,
                ticker_price_time=fa.latest_price_date,
                percentage_of_portfolio=market_value / portfolio.value,
                buy_date=buy_date,
                market_value=market_value if requesting_creator else None,
            )
        )

    return HoldingsResponse(
        portfolio_type=PortfolioType.Creator if requesting_creator else PortfolioType.User, holdings=holdings_res
    )


@router.post("/trading-history", status_code=status.HTTP_200_OK, response_model=TradingHistoryResponse)
async def route_get_trading_history(portfolio_request: PortfolioRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    requesting_creator = False
    if user_id != portfolio_request.user_id:
        subscriber = await get_user_subscription(user_id=user_id, creator_id=portfolio_request.user_id)
        if subscriber is None:
            raise Exception("user is not a subscriber of creator")
        requesting_creator = True

    # Get list of trades
    trade_history = await get_trading_history(portfolio_request.user_id)

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
                transaction_market_value=fat.price * fat.quantity if requesting_creator else None,
                percentage_change_in_position=percentage_change_in_pos,
            )
        )

    return TradingHistoryResponse(
        portfolio_type=PortfolioType.Creator if requesting_creator else PortfolioType.User, trades=trades_res_list
    )


def get_portfolio_value(holdings: list, user_id: str) -> PortfolioValue:
    portfolio_value = PortfolioValue(user_id=user_id, value=0)
    for holding in holdings:
        fa = holding.FinancialAccountCurrentHoldings
        value = portfolio_value.value + Decimal(fa.quantity * fa.latest_price)
        portfolio_value.value = value

    return portfolio_value

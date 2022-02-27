from sqlalchemy import select
from sqlalchemy.sql import Select

from common_amirainvest_com.schemas.schema import Securities, SecurityPrices, Users, WatchlistItems, Watchlists


def watchlist_items_select() -> Select:
    return (
        select(Watchlists, WatchlistItems, Users, SecurityPrices, Securities)
        .outerjoin(Watchlists, Users.id == Watchlists.creator_id)
        .outerjoin(WatchlistItems, WatchlistItems.watchlist_id == Watchlists.id)
        .outerjoin(Securities, Securities.ticker_symbol == WatchlistItems.ticker)
        .outerjoin(SecurityPrices, SecurityPrices.security_id == Securities.id)
    )

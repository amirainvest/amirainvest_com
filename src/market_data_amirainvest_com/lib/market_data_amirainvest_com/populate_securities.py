from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Securities
from common_amirainvest_com.utils import logger
from common_amirainvest_com.utils.decorators import Session
from market_data_amirainvest_com.iex import get_company_info, get_stock_quote, get_supported_securities_list
from market_data_amirainvest_com.models.iex import Symbol


@Session
async def insert_securities(
    session: AsyncSession, supported_securities: list[Symbol], current_securities: dict[str, None]
):
    insertable_securities = []
    for s in supported_securities:
        if s.symbol is None or s.symbol in current_securities:
            continue
        company = await get_company_info(s.symbol)
        if company is None:
            logger.log.info(f"could not fetch company information for {s.symbol}")
            continue

        quote = await get_stock_quote(s.symbol)
        if quote is None:
            logger.log.info(f"could not fetch quote for {s.symbol}")

        insertable_securities.append(
            Securities(
                name=s.name,
                ticker_symbol=s.symbol,
                exchange=s.exchange,
                description=company.description,
                website=company.website,
                industry=company.industry,
                ceo=company.CEO,
                issue_type=company.issueType,
                sector=company.sector,
                primary_sic_code=company.primarySicCode,
                employee_count=company.employees,
                address=company.address,
                phone=company.phone,
                open_price=quote.open,
                close_price=quote.close,
                type=s.type,
                iso_currency_code=quote.currency,
            )
        )
    session.add_all(insertable_securities)


@Session
async def fetch_existing_records(session: AsyncSession, securities: list[Symbol]) -> dict[str, None]:
    symbols = []
    for security in securities:
        symbols.append(security.symbol)

    result = await session.execute(select(Securities).where(Securities.ticker_symbol.in_(symbols)))
    current_internal_securities = result.scalars().all()
    cur_secs_dict: dict[str, None] = {}
    for c_sec in current_internal_securities:
        cur_secs_dict[c_sec.ticker_symbol] = None
    return cur_secs_dict


async def run():
    supported_securities = await get_supported_securities_list()
    current_securities = await fetch_existing_records(supported_securities)
    await insert_securities(current_securities)


if __name__ == "__main__":
    print("Should probably run this...")

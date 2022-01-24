import asyncio
import pprint

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Securities
from common_amirainvest_com.utils import logger
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.decorators import Session
from market_data_amirainvest_com.iex import get_company_info, get_stock_quote, get_supported_securities_list, IEXError
from market_data_amirainvest_com.models.iex import Symbol


failed_things = []


# TODO: Write timeout/limit logic... should retry but sleep if issues(do some type of backoff)?
@Session
async def insert_securities(
    session: AsyncSession, supported_securities: list[Symbol], current_securities: dict[str, None]
):
    grouping = []
    sub_group = []
    for s in supported_securities:
        if s.symbol is None or s.symbol in current_securities:
            continue
        sub_group.append(s)
        if (
                len(sub_group) >= 33
        ):  # We use groups of 50 since we make two api calls / security and we are limited to 100 a second
            grouping.append(sub_group)
            sub_group = []

    total_groups = len(grouping)
    counter = 1
    for group in grouping:
        print(f"Processing {counter}/{total_groups}")
        await asyncio.gather(*(work(params) for params in group))
        print(f"Finished Processing {counter}/{total_groups}")
        await asyncio.sleep(2)
        counter = counter + 1
        await session.commit()


@Session
async def work(session: AsyncSession, s: Symbol):
    try:
        if s.symbol is None or s.symbol == "":
            return

        company = await get_company_info(s.symbol)
        if company is None:
            logger.log.info(f"could not fetch company information for {s.symbol}")
            return

        quote = await get_stock_quote(s.symbol)
        if quote is None:
            logger.log.info(f"could not fetch quote for {s.symbol}")

        open_price = 0
        if quote.open is not None:
            open_price = quote.open

        close_price = 0
        if quote.close is not None:
            close_price = quote.close

        session.add(
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
                open_price=open_price,
                close_price=close_price,
                type=s.type,
                currency=quote.currency,
            )
        )
    except IEXError as err:
        global failed_things
        failed_things.append({'symbol': s.symbol, 'error': err})


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
    await insert_securities(supported_securities, current_securities)


if __name__ == "__main__":
    run_async_function_synchronously(run)
    pprint.pprint(failed_things)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Securities
from common_amirainvest_com.utils.decorators import Session
from market_data_amirainvest_com.iex import get_company_info, get_stock_quote, get_supported_securities_list


@Session
async def run(session: AsyncSession):
    # Populate Securities Table with Security Information & Company Metadata
    # Get Securities List

    supported_securities = []
    try:
        supported_securities = await get_supported_securities_list()
    except Exception as e:
        print(e)

    # Check what securities exist
    supported_security_symbols = []
    for supported_security in supported_securities:
        supported_security_symbols.append(supported_security.symbol)
    # Populate DB with Records
    result = await session.execute(select(Securities).where(Securities.ticker_symbol.in_(supported_security_symbols)))
    current_internal_securities = result.scalars().all()
    current_security_dict: dict[str, None] = {}
    for c_sec in current_internal_securities:
        current_security_dict[c_sec.ticker_symbol] = None

    insertable_securities = []
    for s in supported_securities:
        if s.symbol is None or s.symbol in current_security_dict:
            continue
        company = await get_company_info(s.symbol)
        if company is None:
            # TODO: log something here..
            continue

        quote = await get_stock_quote(s.symbol)
        if quote is None:
            # TODO: log something here...
            continue

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

    # Query DB to get any Missing Data

    # Hit Company info to populate data -- this we could do in async fashion

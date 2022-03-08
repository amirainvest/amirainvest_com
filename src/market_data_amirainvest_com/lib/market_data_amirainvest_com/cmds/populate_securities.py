import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.iex.client import get_company_quote_logo_bulk, get_supported_securities_list
from common_amirainvest_com.iex.model import CompanyQuoteLogo
from common_amirainvest_com.schemas.schema import Securities
from common_amirainvest_com.utils.decorators import Session


@Session
async def insert_securities(session: AsyncSession, supported_securities: list[CompanyQuoteLogo]):
    stuff: dict[str, CompanyQuoteLogo] = {}
    for ss in supported_securities:
        stuff[ss.symbol] = ss

    response = await session.execute(select(Securities).where(Securities.ticker_symbol.in_(stuff.keys())))
    securities: list[Securities] = response.scalars().all()
    for sec in securities:
        new_sec: CompanyQuoteLogo = stuff[sec.ticker_symbol]
        del stuff[sec.ticker_symbol]
        sec.human_readable_name = (
            new_sec.companyName if new_sec.companyName is not None or new_sec.companyName != "" else None
        )

        sec.close_price = new_sec.close if new_sec.close is not None else 0
        sec.name = new_sec.securityName if new_sec.securityName is not None else ""
        sec.open_price = new_sec.open if new_sec.close is not None else 0
        sec.asset_type = new_sec.issueType
        sec.address = new_sec.address
        sec.ceo = new_sec.CEO
        sec.currency = new_sec.currency
        sec.description = new_sec.description
        sec.employee_count = new_sec.employees
        sec.exchange = new_sec.exchange
        sec.industry = new_sec.industry
        sec.issue_type = new_sec.issueType
        sec.phone = new_sec.phone
        sec.primary_sic_code = new_sec.primarySicCode
        sec.sector = new_sec.sector
        sec.website = new_sec.website

    await session.flush()

    values = []
    for key in stuff:
        c = stuff[key]
        if c.symbol is None:
            continue
        values.append(
            Securities(
                human_readable_name=c.companyName,
                ticker_symbol=c.symbol,
                close_price=c.close if c.close is not None else 0,
                name=c.securityName if c.securityName is not None else "",
                open_price=c.open if c.open is not None else 0,
                asset_type=c.issueType,
                address=c.address,
                ceo=c.CEO,
                currency=c.currency,
                description=c.description,
                employee_count=c.employees,
                exchange=c.exchange,
                industry=c.industry,
                issue_type=c.issueType,
                phone=c.phone,
                primary_sic_code=c.primarySicCode,
                sector=c.sector,
                type=c.issueType,
                website=c.website,
            )
        )

    session.add_all(values)


async def run():
    supported_securities = await get_supported_securities_list()

    groups: list[list] = []
    group = []
    for idx, ss in enumerate(supported_securities):
        group.append(ss)
        if len(group) == 100 or idx == len(supported_securities) - 1:
            groups.append(group)
            group = []

    for g in groups:
        companies = await get_company_quote_logo_bulk([s.symbol for s in g])
        await insert_securities(companies)


if __name__ == "__main__":
    asyncio.run(run())

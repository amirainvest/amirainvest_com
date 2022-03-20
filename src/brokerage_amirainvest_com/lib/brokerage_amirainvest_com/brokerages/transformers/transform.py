from brokerage_amirainvest_com.brokerages.transformers import (
    charles_schwab,
    e_trade,
    interactive_brokers,
    merrill_edge,
    robinhood,
    td_ameritrade,
)
from brokerage_amirainvest_com.brokerages.transformers.transformer import BrokerageTransformer
from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccounts,
    FinancialAccountTransactions,
    FinancialInstitutions,
)


async def transform_transactions(
    financial_institution: FinancialInstitutions,
    financial_accounts: list[FinancialAccounts],
    financial_transactions: list[FinancialAccountTransactions],
    financial_holdings: list[FinancialAccountCurrentHoldings],
) -> list[FinancialAccountTransactions]:
    if financial_institution.third_party_institution_id is None:
        raise Exception("no third party institution id provided")

    try:
        brokerage = institution_ids_to_class[financial_institution.third_party_institution_id]
        return await brokerage.transform_transactions(financial_accounts, financial_transactions, financial_holdings)
    except Exception as err:
        raise err


async def transform_accounts(
    financial_institution: FinancialInstitutions,
    financial_accounts: list[FinancialAccounts],
    financial_transactions: list[FinancialAccountTransactions],
    financial_holdings: list[FinancialAccountCurrentHoldings],
) -> list[FinancialAccounts]:
    if financial_institution.third_party_institution_id is None:
        raise Exception("no third party institution id provided")

    try:
        brokerage = institution_ids_to_class[financial_institution.third_party_institution_id]
        return await brokerage.transform_accounts(financial_accounts, financial_transactions, financial_holdings)
    except Exception as err:
        raise err


async def transform_holdings(
    financial_institution: FinancialInstitutions,
    financial_accounts: list[FinancialAccounts],
    financial_transactions: list[FinancialAccountTransactions],
    financial_holdings: list[FinancialAccountCurrentHoldings],
) -> list[FinancialAccountCurrentHoldings]:
    if financial_institution.third_party_institution_id is None:
        raise Exception("no third party institution id provided")

    try:
        brokerage = institution_ids_to_class[financial_institution.third_party_institution_id]
        return await brokerage.transform_holdings(financial_accounts, financial_transactions, financial_holdings)
    except Exception as err:
        raise err


institution_ids_to_class: dict[str, BrokerageTransformer] = {
    "ins_64": robinhood.Robinhood(),
    "ins_115610": merrill_edge.MerrillEdge(),
    "ins_11": charles_schwab.CharlesSchwab(),
    "ins_116530": interactive_brokers.InteractiveBrokers(),
    "ins_129473": e_trade.ETrade(),
    "ins_119423": td_ameritrade.TDAmeritrade(),
}

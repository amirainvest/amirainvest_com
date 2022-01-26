from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from market_data_amirainvest_com.cmds.populate_securities import run


def handler():
    run_async_function_synchronously(run)

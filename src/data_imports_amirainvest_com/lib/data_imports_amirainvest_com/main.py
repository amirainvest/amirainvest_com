import os

from sqs.data_load_consumer import consume_data_load_sqs_queue
from sqs.data_load_producer import load_refresh_ready_data

from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.logger import log


async def run(action: str):
    log.info(f"{action} running.")
    if action == "data_load_consumer":
        consume_data_load_sqs_queue()
    elif action == "expedited_data_load_consumer":
        consume_data_load_sqs_queue(expedited=True)
    elif action == "data_load_refresh_producer":
        await load_refresh_ready_data()
    else:
        raise (ValueError(f"Action environment variable not in options: {action}"))


def sync_run():
    action = os.environ.get("ACTION", None)
    run_async_function_synchronously(run, action)


if __name__ == "__main__":
    sync_run()

import json
from contextlib import contextmanager
from multiprocessing import Process
from time import sleep
from typing import Callable, Optional

import boto3
from mypy_boto3_sqs import SQSServiceResource
from mypy_boto3_sqs.service_resource import Message, Queue
from mypy_boto3_sqs.type_defs import SendMessageResultTypeDef
from pydantic import BaseModel

from common_amirainvest_com.utils.consts import AWS_REGION
from common_amirainvest_com.utils.logger import log


sqs_resource: SQSServiceResource = boto3.resource("sqs", region_name=AWS_REGION)


def get_messages(sqs_queue: Queue, timeout: int = 60) -> list[Message]:
    return sqs_queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=20, VisibilityTimeout=timeout)


def add_message_to_queue(sqs_queue: str, message: BaseModel) -> SendMessageResultTypeDef:
    return sqs_resource.Queue(sqs_queue).send_message(MessageBody=message.json())


def _keep_message_alive(message, timeout: int = 60):
    while True:
        sleep(timeout / 2)
        message.change_visibility(VisibilityTimeout=timeout)


@contextmanager
def keep_message_alive(message: Message, timeout: int = 60, error_queue: Optional[Queue] = None):
    process = Process(target=keep_message_alive, args=(message, timeout), daemon=True)
    process.start()
    try:
        try:
            yield
        finally:
            process.terminate()
            process.join()
            process.close()
    except:  # noqa: E722
        if error_queue is not None:
            error_queue.send_message(MessageBody=message.body)
        raise
    else:
        message.delete()


def consume_queue(queue_name: str, func: Callable, timeout: int = 60, sleep_time: int = 5):
    queue: Queue = sqs_resource.Queue(queue_name)
    while True:
        try:
            message: Message = get_messages(queue, timeout)[0]
            with keep_message_alive(message, timeout):
                data: dict = json.loads(message.body)
                try:
                    log.debug(data)
                    func(**data)
                except:  # noqa: E722
                    log.exception(f"Error running {func} with data {data}")
                    raise

        except IndexError:
            sleep(sleep_time)

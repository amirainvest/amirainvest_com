import json
from multiprocessing import Process
from time import sleep

import boto3

from common_amirainvest_com.utils.logger import log
from data_imports_amirainvest_com.constants import AWS_REGION


sqs_resource: boto3.resource = boto3.resource("sqs", AWS_REGION)


def get_messages(sqs_queue: sqs_resource.Queue, timeout: int = 60) -> list:
    return sqs_queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=20, VisibilityTimeout=timeout)


def add_message_to_queue(sqs_queue: str, message: str):
    sqs_resource.Queue(sqs_queue).send_message(MessageBody=message)


def keep_message_alive(message, timeout: int = 60):
    while True:
        sleep(timeout / 2)
        message.change_visibility(VisibilityTimeout=timeout)


def consume_queue(queue: str, func: callable, timeout: int = 60):
    queue = sqs_resource.Queue(queue)
    while True:
        try:
            message = get_messages(queue, timeout)[0]
            process = Process(target=keep_message_alive, args=(message, timeout), daemon=True)
            process.start()
            data = json.loads(message.body)
            try:
                print(data)
                func(**data)
            except Exception:
                try:
                    raise Exception()
                except Exception:
                    import traceback

                    traceback = f"{traceback.format_exc()}\n\n{str(data)}"
                    log.exception(traceback)
            process.terminate()
            process.join()
            process.close()
            message.delete()
        except IndexError:
            pass

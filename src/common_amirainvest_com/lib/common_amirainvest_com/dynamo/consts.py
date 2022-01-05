import boto3
from mypy_boto3_dynamodb import DynamoDBServiceResource

from common_amirainvest_com.utils.consts import ENVIRONMENT, Environments


__all__ = ["dynamo_resource"]

dynamo_resource: DynamoDBServiceResource = boto3.resource("dynamodb", endpoint_url="http://dynamo:8000")

if ENVIRONMENT == Environments.prod or ENVIRONMENT == Environments.staging:
    dynamo_resource = boto3.resource("dynamodb")

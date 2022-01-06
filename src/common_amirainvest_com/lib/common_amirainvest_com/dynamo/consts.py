import boto3
from mypy_boto3_dynamodb import DynamoDBServiceResource

from common_amirainvest_com.utils.consts import ENVIRONMENT, Environments


__all__ = ["dynamo_resource"]

dynamo_resource: DynamoDBServiceResource

if ENVIRONMENT == Environments.prod.value or ENVIRONMENT == Environments.staging.value:
    dynamo_resource = boto3.resource("dynamodb")
else:
    dynamo_resource = boto3.resource("dynamodb", endpoint_url="http://dynamo:8000")

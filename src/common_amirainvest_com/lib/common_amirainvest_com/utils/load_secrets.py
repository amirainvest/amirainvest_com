import base64
import functools
import typing as t

import boto3
from botocore.exceptions import ClientError
from dotenv import dotenv_values
from mypy_boto3_secretsmanager import SecretsManagerClient
from mypy_boto3_secretsmanager.type_defs import ListSecretsResponseTypeDef


def print_export():
    values = dotenv_values(dotenv_path=".env")
    values = [f"export {key}={val}" for key, val in values.items()]
    print("\n".join(values))


@functools.cache
def _get_all_secret_arns(environment: str = "test", aws_region: str = "us-east-1") -> t.List[str]:
    session = boto3.session.Session()
    client: SecretsManagerClient = session.client(
        service_name='secretsmanager',
        region_name=aws_region
    )
    secret_arn_list: t.List[str] = []
    while True:
        next_token = None
        call_dict = {
            "MaxResults": 100,
            "Filters": [
                {
                    "Key": "tag-key",
                    "Values": ["env"],
                },
                {
                    "Key": "tag-value",
                    "Values": [environment],
                }
            ]
        }
        if next_token is not None:
            call_dict["NextToken"] = next_token

        results: ListSecretsResponseTypeDef = client.list_secrets(
            **call_dict
        )

        secret_arn_list.extend([secret["ARN"] for secret in results["SecretList"]])

        next_token = results.get("NextToken", None)
        if next_token is None:
            break
    return secret_arn_list


def _get_aws_secret_value(secret_arn: str, aws_region: str = "us-east-1") -> t.Tuple[str, str]:
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=aws_region
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_arn
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary']).decode("utf-8")

        return get_secret_value_response["Name"], secret


def _get_all_secret_values(environment: str = "test"):
    secret_arn_list = _get_all_secret_arns(environment)
    for secret_arn in secret_arn_list:
        print(_get_aws_secret_value(secret_arn))


if __name__ == "__main__":
    print_export()

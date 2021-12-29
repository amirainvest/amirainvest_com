import base64
import functools
import os
import typing as t
import warnings

import boto3
from botocore.exceptions import ClientError, CredentialRetrievalError, NoCredentialsError
from dotenv import dotenv_values
from mypy_boto3_secretsmanager import SecretsManagerClient
from mypy_boto3_secretsmanager.type_defs import ListSecretsResponseTypeDef


BASE64_BYPASS = {"ENVIRONMENT", "DEBUG"}


def print_env_vars():
    values_dict = {}

    values = dotenv_values(dotenv_path="local.env")
    for key, value in values.items():
        values_dict[key] = value

    values = dotenv_values(dotenv_path=".env")
    for key, value in values.items():
        values_dict[key] = value

    environment = os.environ.get("ENVIRONMENT", "local")
    project = os.environ.get("PROJECT", "mono")
    try:
        values = _get_all_secret_values(environment, project)
        for key, value in values.items():
            values_dict[key] = value
    except (CredentialRetrievalError, NoCredentialsError):
        warnings.warn("Missing AWS creds", RuntimeWarning)

    final_values = []
    for key, value in values_dict.items():
        if key in BASE64_BYPASS:
            export_string = f"export {key}={value}"
        else:
            b64encoded_string = base64.b64encode(value.encode("UTF-8")).decode("UTF-8")
            export_string = f"export {key}={b64encoded_string}"
        final_values.append(export_string)

    print("\n".join(final_values))


@functools.cache
def _get_all_secret_arns(environment: str = "test", aws_region: str = "us-east-1") -> t.List[str]:
    session = boto3.session.Session()
    client: SecretsManagerClient = session.client(service_name="secretsmanager", region_name=aws_region)
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
                    "Values": [environment, "all"],
                },
            ],
        }
        if next_token is not None:
            call_dict["NextToken"] = next_token

        results: ListSecretsResponseTypeDef = client.list_secrets(**call_dict)  # type: ignore

        secret_arn_list.extend([secret["ARN"] for secret in results["SecretList"]])

        next_token = results.get("NextToken", None)
        if next_token is None:
            break
    return secret_arn_list


def _get_aws_secret_value(secret_arn: str, aws_region: str = "us-east-1") -> t.Tuple[str, str]:
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=aws_region)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_arn)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"]).decode("utf-8")

        return get_secret_value_response["Name"], secret


def _get_all_secret_values(environment: str = "test", project: str = "all") -> t.Dict[str, str]:
    secret_arn_list = _get_all_secret_arns(environment)
    secrets_dict = {}
    for secret_arn in secret_arn_list:
        secret_tuple = _get_aws_secret_value(secret_arn)
        secret_name, secret_value = secret_tuple

        cleaned_name = None
        if secret_name.startswith(f"{project}-"):
            cleaned_name = secret_name.split(f"{project}-", 1)[1]
        elif secret_name.startswith(f"{environment}-"):
            cleaned_name = secret_name.split(f"{environment}-", 1)[1]

        if cleaned_name is not None:
            secrets_dict[cleaned_name] = secret_value

    return secrets_dict


if __name__ == "__main__":
    print_env_vars()

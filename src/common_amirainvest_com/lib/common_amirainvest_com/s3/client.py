from io import BytesIO

import boto3
import botocore.exceptions
from mypy_boto3_s3 import S3ServiceResource


class S3:
    resource: S3ServiceResource

    def __init__(self):
        self.resource = boto3.resource("s3")

    async def upload_file(self, local_filepath: str, bucket: str, key: str) -> str:
        self.resource.meta.client.upload_file(local_filepath, bucket, key)
        return build_s3_url(bucket, key)

    # TODO: What should we use for the type hint on file_bytes??
    async def upload_file_by_bytes(self, file_bytes, bucket: str, key: str):
        self.resource.Bucket(bucket).upload_fileobj(Fileobj=BytesIO(file_bytes), Key=key)
        return build_s3_url(bucket, key)

    async def download_object(self, local_filepath: str, bucket: str, key: str):
        with open(local_filepath, "wb") as data:
            self.resource.meta.client.download_fileobj(bucket, key, data)

    async def validate_object_exists(self, bucket: str, key: str) -> bool:
        try:
            self.resource.meta.client.head_object(
                Bucket=bucket,
                Key=key,
            )
            return True
        except botocore.exceptions.ClientError as err:
            if err.response["Error"]["Message"] == "Not Found":
                return False
            raise err


def build_s3_url(bucket, s3_filepath):
    return f"https://s3.amazonaws.com/{bucket}/{s3_filepath}"

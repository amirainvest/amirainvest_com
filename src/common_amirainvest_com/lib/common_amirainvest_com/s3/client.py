from io import BytesIO
from typing import Optional

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

    async def get_all_objects(self, bucket_name: str, prefix: Optional[str], start_after: Optional[str]):
        response = self.resource.meta.client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix if prefix is not None else "",
            StartAfter=start_after if start_after is not None else "",
        )

        if "Contents" not in response:
            return None
        return response["Contents"]

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

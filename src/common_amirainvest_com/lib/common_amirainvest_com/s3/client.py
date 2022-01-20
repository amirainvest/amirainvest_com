from io import BytesIO

import boto3


class S3:
    def __init__(self):
        self.s3_resource = boto3.resource("s3")
        self.s3_client = boto3.client("s3")

    async def upload_file(self, local_filepath, bucket, s3_filepath):
        self.s3_resource.meta.client.upload_file(local_filepath, bucket, s3_filepath)
        return build_s3_url(bucket, s3_filepath)

    async def upload_file_by_bytes(self, file_bytes, s3_filepath, bucket):
        self.s3_resource.Bucket(bucket).upload_fileobj(Fileobj=BytesIO(file_bytes), Key=s3_filepath)
        return build_s3_url(bucket, s3_filepath)


def build_s3_url(bucket, s3_filepath):
    return f"https://s3.amazonaws.com/{bucket}/{s3_filepath}"
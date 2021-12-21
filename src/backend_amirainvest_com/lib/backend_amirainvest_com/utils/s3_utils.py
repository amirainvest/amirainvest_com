import boto3  # type: ignore


class S3:
    def __init__(self):
        self.s3_resource = boto3.resource("s3")
        self.s3_client = boto3.client("s3")

    def upload_file(self, local_filepath, bucket, s3_filepath):
        self.s3_resource.meta.client.upload_file(local_filepath, bucket, s3_filepath)
        return f"https://s3.amazonaws.com/{bucket}/{s3_filepath}"

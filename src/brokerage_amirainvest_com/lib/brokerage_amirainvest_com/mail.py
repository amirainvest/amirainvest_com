# type: ignore
import boto3

# type: ignore
from botocore.exceptions import ClientError


# TODO: Move to common and pass in a body, text body, subject, & list of recipients
class MailService:
    region: str
    sender: str
    client = None

    def __init__(self, sender: str, aws_region: str = "us-east-1"):
        self.client = boto3.client("ses", region_name=aws_region)
        self.sender = sender

    def send_historical_mail(self, recipient: str):
        body = """
            <html>
            <head></head>
            <body>
                <h1> Processing Finished </h1>
                <p>We've finished processing your account and all brokerage is up to date</p>
            </body>
            </html>
        """
        body_text = """"""

        subject = """AmiraInvest Brokerage Processing Finished"""

        try:
            response = self.client.send_email(
                Destination={"ToAddresses": [recipient]},
                Message={
                    "Body": {
                        "Html": {"Charset": "UTF-8", "Data": body},
                        "Text": {"Charset": "UTF-8", "Data": body_text},
                    },
                    "Subject": {"Charset": "UTF-8", "Data": subject},
                },
                Source=self.sender,
                # ConfigurationSetName=''
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
        else:
            print("Email sent! MEssage ID:")
            print(response["MessageId"])

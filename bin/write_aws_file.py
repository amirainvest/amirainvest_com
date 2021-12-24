import os


config = """
[default]
region = us-east-1
output = json
"""

creds = f"""
[default]
aws_access_key_id = {os.environ["AWS_ACCESS_KEY_ID"]}
aws_secret_access_key = {os.environ["AWS_SECRET_ACCESS_KEY"]}
"""

with open("~/.aws/credentials") as f:
    f.write(creds)

with open("~/.aws/config") as f:
    f.write(config)

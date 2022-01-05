from typing import Optional

from common_amirainvest_com.dynamo.consts import dynamo_resource  # type: ignore
from common_amirainvest_com.dynamo.models import BrokerageUser  # type: ignore


# Using this as a catch-all for the time being, but thinking we come up with a service package or something
# e.g., brokerage.py for dynamo queries to persist and be used across application


async def create_table(table_name: str, key_name: str):
    try:
        table = dynamo_resource.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": key_name, "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": key_name, "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        table_status = table.table_status
        while table_status != "ACTIVE":
            brokerage_user = dynamo_resource.Table("brokerage_user")
            table_status = brokerage_user.table_status
    except Exception as e:
        print(e)


async def update_brokerage_user(brokerage_user: BrokerageUser):
    table = dynamo_resource.Table("brokerage_users")
    table.update_item(
        Key={"user_id": brokerage_user.user_id},
        ReturnValues="NONE",
        UpdateExpression="set plaid_access_tokens=:p",
        ExpressionAttributeValues={":p": brokerage_user.plaid_access_tokens},
    )


async def add_brokerage_user(brokerage_user: BrokerageUser):
    item = {
        "user_id": brokerage_user.user_id,
        "plaid_access_tokens": brokerage_user.plaid_access_tokens,
    }
    table = dynamo_resource.Table("brokerage_users")
    table.put_item(Item=item)


async def get_brokerage_user(user_id: str) -> Optional[BrokerageUser]:
    table = dynamo_resource.Table("brokerage_users")
    brokerage_user = table.get_item(Key={"user_id": user_id})
    if "Item" not in brokerage_user:
        return None
    return BrokerageUser(**brokerage_user["Item"])

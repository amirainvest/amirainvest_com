import asyncio
from typing import Optional

from boto3.dynamodb.conditions import Key

from common_amirainvest_com.dynamo.consts import dynamo_resource
from common_amirainvest_com.dynamo.models import BrokerageUser


# Using this as a catch-all for the time being, but thinking we come up with a service package or something
# e.g., brokerage.py for dynamo queries to persist and be used across application


async def create_table(table_name: str, partition_key: str, sort_key: Optional[str]):
    try:
        key_schema = [{"AttributeName": partition_key, "KeyType": "HASH"}]
        attribute_definitions = [{"AttributeName": partition_key, "AttributeType": "S"}]
        if sort_key is not None:
            key_schema.append({"AttributeName": sort_key, "KeyType": "RANGE"})
            attribute_definitions.append({"AttributeName": sort_key, "AttributeType": "S"})

        table = dynamo_resource.create_table(
            TableName=table_name,
            KeySchema=key_schema,  # type: ignore
            AttributeDefinitions=attribute_definitions,  # type: ignore
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
        Key={"user_id": brokerage_user.user_id, "item_id": brokerage_user.item_id},
        ReturnValues="NONE",
        UpdateExpression="set access_token=:p",
        ExpressionAttributeValues={":p": brokerage_user.access_token},
    )


async def add_brokerage_user(brokerage_user: BrokerageUser):
    item = {
        "user_id": brokerage_user.user_id,
        "item_id": brokerage_user.item_id,
        "access_token": brokerage_user.access_token,
    }

    table = dynamo_resource.Table("brokerage_users")
    response = table.put_item(Item=item)  # type: ignore
    return response


async def get_brokerage_user_item(user_id: str, item_id: str) -> Optional[BrokerageUser]:
    table = dynamo_resource.Table("brokerage_users")
    brokerage_user = table.get_item(Key={"user_id": user_id, "item_id": item_id})
    item = brokerage_user.get("Item")
    if item is None:
        return None
    return BrokerageUser.parse_obj(item)


async def get_brokerage_user_items(user_id: str) -> Optional[list[BrokerageUser]]:
    table = dynamo_resource.Table("brokerage_users")
    brokerage_user_items = table.query(KeyConditionExpression=Key("user_id").eq(user_id))
    items = brokerage_user_items.get("Items")
    if items is None or len(items) <= 0:
        return None
    return [BrokerageUser.parse_obj(item) for item in items]


async def run():
    await create_table("brokerage_users", "user_id", "item_id")


if __name__ == "__main__":
    asyncio.run(run())

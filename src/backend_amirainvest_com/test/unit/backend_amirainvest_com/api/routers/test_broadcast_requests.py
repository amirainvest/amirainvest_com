pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
import datetime
import json

import pytest

from common_amirainvest_com.utils.test.factories.schema import BroadcastRequestsFactory, UsersFactory

from .config import client


@pytest.mark.asyncio
async def test_not_authenticated_get_broadcast_requests():
    response = client.get("/broadcast_requests/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_broadcast_requests_for_creator():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    broadcast_request = await BroadcastRequestsFactory(subscriber_id=subscriber.id, creator_id=creator.id)
    response = client.get("/broadcast_requests/")
    assert response.status_code == 200
    response_data = response.json()
    assert type(response_data) == list
    assert broadcast_request.id in [x.id for x in response_data]
    response_broadcast_request = response_data[0]
    assert response_broadcast_request["creator_id"] == creator.id
    assert response_broadcast_request["subscriber_id"] == subscriber.id


@pytest.mark.asyncio
async def test_create_broadcast_request():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    response = client.post(
        "/broadcast_requests/",
        json.dumps(
            {"subscriber_id": subscriber.id, "creator_id": creator.id, "created_at": datetime.datetime.utcnow()}
        ),
    )
    print(response)

pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
from common_amirainvest_com.utils.test.factories.schema import UsersFactory, UserSubscriptionsFactory

from .config import client


def test_not_authenticated_get_user_subscriptions():
    response = client.get("/user_subscriptions/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_subscriptions_for_subscriber():
    subscriber = await UsersFactory()
    creator = await UsersFactory()
    await UserSubscriptionsFactory(creator_id=creator.id, subscriber_id=subscriber.id)
    response = client.get("/user_subscriptions/subscriber/", params={"subscriber_id": subscriber.id})
    assert response.status_code == 200
    assert creator.id in [x.creator_id for x in response.json()]


def test_get_subscriptions_for_creator():
    subscriber = await UsersFactory()
    creator = await UsersFactory()
    await UserSubscriptionsFactory(creator_id=creator.id, subscriber_id=subscriber.id)
    response = client.get("/user_subscriptions/creator/", params={"subscriber_id": subscriber.id})
    assert response.status_code == 200
    assert subscriber.id in [x.subscriber_id for x in response.json()]


def test_create_subscription():
    subscriber = await UsersFactory()
    await UsersFactory()
    client.get("/user_subscriptions/subscribe/", params={"subscriber_id": subscriber.id})

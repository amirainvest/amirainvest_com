from .config import client


def test_not_authenticated_get_user_subscriptions():
    response = client.get("/user_subscriptions/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}

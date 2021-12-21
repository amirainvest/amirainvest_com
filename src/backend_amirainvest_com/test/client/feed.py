from .config import client


def test_not_authenticated_get_feed():
    response = client.get("/feed/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}

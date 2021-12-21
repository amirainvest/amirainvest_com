from .config import client


def test_not_authenticated_get_broadcast_requests():
    response = client.get("/broadcast_requests/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}

from .config import client


def test_not_authenticated_get_husk_requests():
    response = client.get("/husk_requests/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}

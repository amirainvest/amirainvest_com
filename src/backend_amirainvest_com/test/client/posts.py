from .config import client


def test_not_authenticated_get_post():
    response = client.get("/post/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}

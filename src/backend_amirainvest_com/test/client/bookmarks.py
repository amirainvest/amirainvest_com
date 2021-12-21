from .config import client


def test_not_authenticated_get_bookmarks():
    response = client.get("/bookmarks/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}

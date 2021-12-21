from .config import client


def test_not_authenticated_get_search_results():
    response = client.get("/search/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}

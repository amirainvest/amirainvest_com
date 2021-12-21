from .config import client


def test_non_authenticated_user_get_code_challenge():
    response = client.get("/code_challenge/")
    assert response.status_code == 200

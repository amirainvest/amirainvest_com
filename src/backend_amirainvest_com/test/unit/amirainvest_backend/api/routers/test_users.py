pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
from .config import client


def test_not_authenticated_get_user():
    response = client.get("/user/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


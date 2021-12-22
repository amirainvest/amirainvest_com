# pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
# import pytest
#
# from .config import client
#
#
# @pytest.mark.asyncio
# async def test_not_authenticated_get_search_results():
#     response = client.get("/search/")
#     assert response.status_code == 403
#     assert response.json() == {"detail": "Not authenticated"}

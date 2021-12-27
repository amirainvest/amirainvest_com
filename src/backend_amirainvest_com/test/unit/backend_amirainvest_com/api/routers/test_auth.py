pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import pytest
from fastapi.security import HTTPBearer
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app

from .config import AUTH_HEADERS, FAKE_AUTH_HEADER


routes_with_no_auth_required_path = [
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
    "/admin/health_check",
    "/code_challenge/",
    "/",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("route", app.routes)
async def test_not_authenticated_get_user(route):
    print(route.name)
    try:
        dependant = route.dependant
        dependencies = dependant.dependencies

        if len(dependencies) == 0:
            assert route.path in routes_with_no_auth_required_path
        for method in route.methods:
            for dep in dependencies:
                try:
                    sub_dep = dep.dependencies[0]
                    if sub_dep.name == "bearer_auth_creds":
                        assert type(sub_dep.call) == HTTPBearer
                        async with AsyncClient(app=app, base_url="http://test") as async_client:
                            client_attr = getattr(async_client, method.lower())

                            no_auth_response = await client_attr(route.path)
                            assert no_auth_response.status_code == 403
                            assert no_auth_response.json() == {"detail": "Not authenticated"}

                            fake_auth_header_response = await client_attr(route.path, headers=FAKE_AUTH_HEADER)
                            assert fake_auth_header_response.status_code == 403
                            assert fake_auth_header_response.json() == {"detail": "Not authenticated"}

                            auth_response = await client_attr(route.path, headers=AUTH_HEADERS)
                            assert auth_response.status_code in {200, 422}
                        break
                except IndexError:
                    pass
            else:
                assert route.path in routes_with_no_auth_required_path
    except (AttributeError, IndexError):
        assert route.path in routes_with_no_auth_required_path

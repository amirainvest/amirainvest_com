from fastapi import status
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app


async def test_config(factory):
    await factory.gen("chip_labels", {"chip_labels": {"name": "Test chip"}})
    await factory.gen("trading_strategies", {"trading_strategies": {"name": "Test trading"}})
    await factory.gen("securities", {"securities": {"is_benchmark": True, "benchmark_alias": "Test benchmark"}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/application/config/get")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    assert response_data

    assert all([x in response_data for x in ["chip_labels", "benchmarks", "trading_strategies"]])

    assert type(response_data["chip_labels"]) == list
    assert type(response_data["trading_strategies"]) == list
    assert type(response_data["benchmarks"]) == list

    assert response_data["chip_labels"][0] == "Test chip"
    assert response_data["trading_strategies"][0] == "Test trading"
    assert response_data["benchmarks"][0]["benchmark"] == "Test benchmark"

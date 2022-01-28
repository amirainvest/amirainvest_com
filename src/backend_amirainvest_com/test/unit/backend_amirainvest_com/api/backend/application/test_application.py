from fastapi import status
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.utils.test.factories.schema import (
    BenchmarksFactory,
    ChipLabelsFactory,
    TradingStrategiesFactory,
)


async def test_config():
    await ChipLabelsFactory(name="Test chip")
    await BenchmarksFactory(name="Test benchmark")
    await TradingStrategiesFactory(name="Test trading")

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/application/config/get")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    assert response_data

    assert all([x in response_data for x in ["chip_labels", "benchmarks", "trading_strategies"]])

    assert type(response_data["chip_labels"]) == list
    assert type(response_data["benchmarks"]) == list
    assert type(response_data["trading_strategies"]) == list

    assert response_data["chip_labels"][0] == "Test chip"
    assert response_data["benchmarks"][0] == "Test benchmark"
    assert response_data["trading_strategies"][0] == "Test trading"

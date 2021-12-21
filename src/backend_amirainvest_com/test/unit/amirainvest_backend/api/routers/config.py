from fastapi.testclient import TestClient

from backend_amirainvest_com.api.app import app
from backend_amirainvest_com.controllers.auth import get_token


client = TestClient(app)

AUTHENTICATION_HEADERS = {"Authentication": f"Bearer {get_token()}"}

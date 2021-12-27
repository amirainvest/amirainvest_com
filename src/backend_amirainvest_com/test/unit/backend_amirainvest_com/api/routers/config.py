from backend_amirainvest_com.controllers.auth import get_application_token


AUTH_HEADERS = {"Authorization": f"Bearer {get_application_token()}"}
FAKE_AUTH_HEADER = {"Authorization": "Bearer FAKE"}

from ..tools import decode_env_var


_auth0_dict = decode_env_var("auth0")
AUTH0_API_AUDIENCE = _auth0_dict["api_audience"]
AUTH0_CLIENT_ID = _auth0_dict["client_id"]
AUTH0_CLIENT_SECRET = _auth0_dict["client_secret"]
AUTH0_DOMAIN = _auth0_dict["domain"]

_auth0_management_dict = decode_env_var("auth0_management")
AUTH0_MANAGEMENT_API_AUDIENCE = _auth0_management_dict["api_audience"]
AUTH0_MANAGEMENT_CLIENT_ID = _auth0_management_dict["client_id"]
AUTH0_MANAGEMENT_CLIENT_SECRET = _auth0_management_dict["client_secret"]
AUTH0_MANAGEMENT_DOMAIN = _auth0_management_dict["domain"]

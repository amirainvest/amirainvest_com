from json import JSONDecodeError

import pkg_resources
import plaid  # type: ignore
import sentry_sdk
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.utils import BadDsn

from .env_vars import DEBUG, ENVIRONMENT, Environments, PROJECT
from .tools import decode_env_var


try:
    integrations = [SqlalchemyIntegration(), RedisIntegration()]

    if PROJECT == "brokerage" or PROJECT == "market_data":
        from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
        integrations.append(AwsLambdaIntegration(timeout_warning=True))

    SENTRY_URL = "https://{public_key}@{domain}/{project_id}".format(**decode_env_var("sentry"))

    sentry_sdk.init(
        SENTRY_URL,
        environment=ENVIRONMENT,
        sample_rate=1.0,
        traces_sample_rate=1.0,
        request_bodies="always",
        integrations=integrations,
        debug=True if DEBUG == "true" else False,
        release=pkg_resources.get_distribution("common_amirainvest_com").version,
    )
except (BadDsn, JSONDecodeError):
    if ENVIRONMENT != Environments.local.value:
        raise EnvironmentError("Sentry URL not set for non local env")

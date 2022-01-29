import os
from enum import Enum


class Environments(Enum):
    prod = "prod"
    staging = "staging"
    local = "local"


class Projects(Enum):
    mono = "mono"
    backend = "backend"
    brokerage = "brokerage"
    market_data = "market_data"


DEBUG = os.environ.get("DEBUG", "true").strip().lower()
ENVIRONMENT = Environments[os.environ.get("ENVIRONMENT", "local").strip().lower()].value
PROJECT = Projects[os.environ.get("PROJECT", "mono").strip().lower()].value

MAX_FEED_SIZE = 200
AWS_REGION = "us-east-1"

COMMON_ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src/common_amirainvest_com")[0]

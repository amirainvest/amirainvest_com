#!/bin/bash

(export ENVIRONMENT="$1" && eval "$(poetry run python -m common_amirainvest_com.utils.load_secrets)" && poetry run alembic upgrade head)

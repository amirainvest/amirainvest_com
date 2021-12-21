#!/bin/sh

set -e

. $VIRTUALENV_PATH/bin/activate

if [ "$DEBUG" == "true" ]; then
  export PYTHONDEVMODE=1
  export PYTHONTRACEMALLOC=1
  export SQLALCHEMY_WARN_20=1
fi

eval "$(python -m common_amirainvest_com.utils.load_secrets)"
exec "$@"

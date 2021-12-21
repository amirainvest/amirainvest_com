#!/bin/sh

set -e

. $VIRTUALENV_PATH/bin/activate

if [ "$DEBUG" == "true" ]; then
  export PYTHONDEVMODE=1
  export PYTHONTRACEMALLOC=1
fi

eval "$(python -m amirainvest_com_common.utils.load_secrets)"
exec "$@"

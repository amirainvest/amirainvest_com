# Environment management

## Running code locally

When running code locally, using either `make interactive` or pycharm run/debug, you can point your local docker
containers at any environment including production.
To change what env your local code is pointing to:


* Open `docker-compose.yaml`
* Under `amirainvest_com` -> `environment:` change `ENVIRONMENT` to point to `test/staging/prod`
* If pointing to `prod`, open `src/common_amirainvest_com/lib/common_amirainvest_com/utils/consts.py` and comment out lines 63-85. To prevent Sentry from causing errors

NOTE: Even when `ENVIRONMENT` says `local` we attempt to pull AWS secrets! The only secrets loaded will be ones tagged
as `env:local` and starting with `local-`. For instance there is a `local-auth0` secret stored to make local testing
possible.

NOTE: When running in the `local` environment, do NOT do so while on the VPN.
It will route all container traffic through amazon servers which may break services


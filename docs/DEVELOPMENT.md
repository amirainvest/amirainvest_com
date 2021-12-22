# Environment management

## Running code locally

When running code locally, using either `make interactive` or pycharm run/debug, you can point your local docker
containers at any environment including production. To change what env your local code is pointing to:


* Open `docker-compose.yaml`
* Under `amirainvest_com` -> `environment:` change `ENVIRONMENT` to point to `test/staging/prod`


NOTE: Even when `ENVIRONMENT` says `local` we attempt to pull AWS secrets! The only secrets loaded will be ones tagged
as `env:local` and starting with `local-`. For instance there is a `local-auth0` secret stored to make local testing
possible.

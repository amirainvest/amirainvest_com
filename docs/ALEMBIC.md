# Run migrations on production

* Git checkout main
* Git pull latest main
* Connect to the VPN (sorry...)
* Run `./bin/run_alembic_migrations.sh <env to run migrations on>`
    * IE: `./bin/run_alembic_migrations.sh prod`
* Disconnect from the VPN

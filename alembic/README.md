Alembic can be used to take your current DB state and compare it with your schema files. Alembic
then generates a delta to get your DB from its current state to the desired state based on the
schema files.

Go into a shell with the PG db connected

`make interactive`

This will generate a script based on the schema - db diff. Replace <description> with a short
description of what has changed in the schemas.

`alembic revision --autogenerate -m "<description>"`

This will run all the db migrations. THIS WILL NOT LOAD ANY DATA. It just changes the table schemas.

`alembic upgrade head`

If you want to go back to a previous db schema state run this.

`alembic downgrade -1`

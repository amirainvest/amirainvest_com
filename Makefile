export
UID="$(shell id -u)"
DOCKER_BUILDKIT=1
BUILDKIT_PROGRESS=plain

.PHONY: check run interactive test db_only initialize_pg run_migrations kill_all_containers remove_all_docker_data _down _base _remove_all_pg_data _insert_pg_data

check:
	poetry install
	poetry run isort src/
	poetry run black src/
	poetry run flake8 src/
	poetry run mypy src/

check_docker: _down
	docker-compose  build --build-arg USER_UID=$(UID) --progress plain simple
	docker-compose  -f docker-compose.yaml run --rm simple isort --check src/
	docker-compose  -f docker-compose.yaml run --rm simple black --check  src/
	docker-compose  -f docker-compose.yaml run --rm simple flake8 src/
	docker-compose  -f docker-compose.yaml run --rm simple mypy src/


### Commands to start docker containers and interact with them
# Starts a shell in the Dockerfile. This is used to run migrations or other commands in the same env as the code
interactive: _down
	docker-compose  build --build-arg USER_UID=$(UID) --progress plain amirainvest_com
	docker-compose  -f docker-compose.yaml -f docker-compose.interactive.yaml run --service-ports --rm amirainvest_com

pycharm: _down
	poetry run python ./bin/fix_pycharm_dirs.py
	docker-compose build --build-arg USER_UID=$(UID) --progress plain amirainvest_com_pycharm

test: initialize_pg _down
	docker-compose build --build-arg USER_UID=$(UID) --progress plain unit_test_amirainvest_com
	docker-compose  -f docker-compose.yaml run --rm unit_test_amirainvest_com

	docker-compose build --build-arg USER_UID=$(UID) --progress plain integration_test_amirainvest_com
	docker-compose  -f docker-compose.yaml run -e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) -e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) --service-ports --rm integration_test_amirainvest_com

backend:
	docker-compose  build --build-arg USER_UID=$(UID) --progress plain backend_amirainvest_com
	docker-compose  -f docker-compose.yaml -f docker-compose.yaml run --service-ports --rm backend_amirainvest_com
# Just starts the postgres DB.
db_only: _down
	docker-compose  -f docker-compose.yaml up --abort-on-container-exit --remove-orphans postgres


### Commands to alter postgres data
# Runs the db migrations and inserts test data
initialize_pg: _down _remove_all_pg_data run_migrations
	$(MAKE) _down

run_migrations: _down
	docker-compose  build --build-arg USER_UID=$(UID) --progress plain amirainvest_com
	docker-compose  -f docker-compose.yaml run --rm amirainvest_com alembic upgrade head
	$(MAKE) _down

### Commands to work with docker

kill_all_containers:
	docker-compose down --remove-orphans
	docker ps -q | xargs -r docker kill

remove_all_docker_data: kill_all_containers
	docker system prune -a -f --volumes


### Commands starting with _ are not to be used in the CLI, but used in other make commands
_down:
	docker-compose  down --remove-orphans

_remove_all_pg_data:
	docker volume rm -f amirainvest_com_common_postgres_data

_insert_pg_data: _down
	docker-compose  -f docker-compose.yaml  -f docker-compose.pg.yaml up -d postgres
	sleep 5
	docker-compose exec postgres psql $(PGDATABASE) $(PGUSER) -f /docker-entrypoint-initdb.d/pg_inserts.sql

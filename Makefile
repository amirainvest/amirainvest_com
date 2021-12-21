include local.env
export
env_file_name="local.env"
UID="$(shell id -u)"
POETRY_PASSWORD="$(shell aws codeartifact get-authorization-token --domain amira-pypi --domain-owner 903791206266 --query authorizationToken --output text)"
POETRY_PUBLISH_URL="$(shell aws codeartifact get-repository-endpoint --domain amira-pypi --domain-owner 903791206266 --repository amira_pypi --format pypi --query 'repositoryEndpoint' --output text)"
DOCKER_BUILDKIT=1
BUILDKIT_PROGRESS=plain

.PHONY: check run interactive test db_only initialize_pg run_migrations kill_all_containers remove_all_docker_data _build _down _base _remove_all_pg_data _insert_pg_data

check:
	poetry run isort tests/ src/
	poetry run black tests/ src/
	poetry run flake8 tests/ src/
	poetry run mypy tests/ src/

check_docker:_base
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml run --rm simple isort --check tests/ src/
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml run --rm simple black --check tests/ src/
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml run --rm simple flake8 tests/ src/
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml run --rm simple mypy --namespace-packages tests/ src/
### Commands to start docker containers and interact with them

publish: _base
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml run --rm publish
run: _base
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml run --service-ports --rm amirainvest_com_common
# Starts a shell in the Dockerfile. This is used to run migrations or other commands in the same env as the code
interactive: _base
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml -f docker-compose.interactive.yaml run --service-ports --rm amirainvest_com_common

test: initialize_pg _base
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml -f docker-compose.test.yaml run --service-ports --rm amirainvest_com_common

# Just starts the postgres DB.
db_only: _base
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml up --abort-on-container-exit --remove-orphans postgres


### Commands to alter postgres data

# Runs the db migrations and inserts test data
initialize_pg: _base _remove_all_pg_data run_migrations
	$(MAKE) _down

run_migrations: _down
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml run --rm amirainvest_com_common alembic upgrade head
	$(MAKE) _down


build_postgres_docker: initialize_pg
	sudo chown -R "$(shell whoami)" ./data
	export DOCKER_BUILDKIT=1 && docker build -f database.Dockerfile -t amirainvest/common/postgres:"$(shell poetry version -s)" .

### Commands to work with docker

kill_all_containers:
	docker-compose down --remove-orphans
	docker ps -q | xargs -r docker kill

remove_all_docker_data: kill_all_containers
	docker system prune -a -f --volumes


### Commands starting with _ are not to be used in the CLI, but used in other make commands

_build:
	docker-compose --env-file $(env_file_name) build --build-arg USER_UID=$(UID) --build-arg POETRY_HTTP_BASIC_AMIRAPYPI_PASSWORD=$(POETRY_PASSWORD) --build-arg POETRY_REPOSITORIES_AMIRAPYPI_URL=$(POETRY_PUBLISH_URL) --build-arg AWS_ACCESS_KEY_ID=$(shell bash ./bin/aws_secrets.sh AWS_ACCESS_KEY_ID) --build-arg AWS_SECRET_ACCESS_KEY=$(shell bash ./bin/aws_secrets.sh AWS_SECRET_ACCESS_KEY) --build-arg SYS_ARCH=$(shell uname -m) --progress plain

_down:
	docker-compose --env-file $(env_file_name) down --remove-orphans

_base: _down _build

_remove_all_pg_data:
	docker volume rm -f common_common_postgres_data

_insert_pg_data: _down
	docker-compose --env-file $(env_file_name) -f docker-compose.yaml  -f docker-compose.pg.yaml up -d postgres
	sleep 5
	docker-compose exec postgres psql $(PGDATABASE) $(PGUSER) -f /docker-entrypoint-initdb.d/pg_inserts.sql

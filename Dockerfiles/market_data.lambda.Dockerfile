# Latest python 3.9-slim
FROM python:3.9 as base

WORKDIR /function

ENV PROJECT_NAME="market_data_amirainvest_com"
ENV PROJECT="market_data"
ENV AWS_DEFAULT_REGION="us-east-1"
ENV POETRY_VIRTUALENVS_CREATE="false"

RUN pip install --target /function awslambdaric
RUN pip install poetry

COPY ./src/$PROJECT_NAME/poetry.lock ./src/$PROJECT_NAME/pyproject.toml ./src/$PROJECT_NAME/
COPY ./src/$PROJECT_NAME/lib/$PROJECT_NAME/__init__.py \
./src/$PROJECT_NAME/lib/$PROJECT_NAME/

COPY ./src/common_amirainvest_com/poetry.lock ./src/common_amirainvest_com/pyproject.toml \
./src/common_amirainvest_com/

COPY ./src/common_amirainvest_com/lib/common_amirainvest_com/__init__.py \
./src/common_amirainvest_com/lib/common_amirainvest_com/

ARG NO_DEV="-v"
WORKDIR ./src/$PROJECT_NAME/

RUN poetry install --no-dev

WORKDIR /function

COPY ./src/$PROJECT_NAME/ ./src/$PROJECT_NAME/
COPY ./src/common_amirainvest_com/ ./src/common_amirainvest_com/
COPY ./local.env ./local.env

ENV AWS_LAMBDA_RUNTIME_API=python3.9
ADD ./src/$PROJECT_NAME/lib/$PROJECT_NAME/aws-lambda-rie-arm64 /usr/local/bin/aws-lambda-rie


# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
ENTRYPOINT ["/bin/bash", "./src/market_data_amirainvest_com/entrypoint.sh"]

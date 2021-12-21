FROM python@sha256:f44726de10d15558e465238b02966a8f83971fd85a4c4b95c263704e6a6012e9 as base

WORKDIR /opt

ARG USER_UID=1000
RUN adduser --shell /bin/sh --system --group --uid "${USER_UID}" default

RUN chown -R default /opt

USER default

ENV VIRTUALENV_PATH="/home/default/venv"
ENV PATH "/home/default/.local/bin:$PATH"

FROM base as final

RUN python -m venv $VIRTUALENV_PATH
RUN pip install poetry

COPY --chown=default:default poetry.lock pyproject.toml ./
RUN mkdir -p ./src/amirainvest_com_common/ && touch ./src/amirainvest_com_common/__init__.py

USER root

ARG SYS_ARCH

RUN if [ "$SYS_ARCH" = "arm64" ] ; then curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip" ; else curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" ; fi
RUN unzip awscliv2.zip  &&    ./aws/install

USER default

ARG NO_DEV="-v"
ARG POETRY_HTTP_BASIC_AMIRAPYPI_USERNAME="aws"

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

RUN export POETRY_HTTP_BASIC_AMIRAPYPI_PASSWORD="$(aws codeartifact get-authorization-token --region us-east-1 --domain amira-pypi --domain-owner 903791206266 --query authorizationToken --output text)" && \
    . $VIRTUALENV_PATH/bin/activate &&  \
    poetry install --remove-untracked "$NO_DEV"

COPY --chown=default:default . .

ARG DEBUG="true"
ENV DEBUG=$DEBUG

ARG ENVIRONMENT="local"
ENV ENVIRONMENT=$ENVIRONMENT

ENV SQLALCHEMY_WARN_20=1

ARG POETRY_HTTP_BASIC_AMIRAPYPI_USERNAME="aws"
ENV POETRY_HTTP_BASIC_AMIRAPYPI_USERNAME=$POETRY_HTTP_BASIC_AMIRAPYPI_USERNAME

ARG POETRY_HTTP_BASIC_AMIRAPYPI_PASSWORD
ENV POETRY_HTTP_BASIC_AMIRAPYPI_PASSWORD=$POETRY_HTTP_BASIC_AMIRAPYPI_PASSWORD

ARG POETRY_REPOSITORIES_AMIRAPYPI_URL
ENV POETRY_REPOSITORIES_AMIRAPYPI_URL=$POETRY_REPOSITORIES_AMIRAPYPI_URL

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
CMD ["python", "src/amirainvest_com_common/main.py"]

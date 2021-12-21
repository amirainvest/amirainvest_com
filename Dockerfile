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
RUN /home/default/venv/bin/python -m pip install --upgrade pip
RUN pip install poetry

COPY --chown=default:default poetry.lock pyproject.toml ./

COPY --chown=default:default ./src/common_amirainvest_com/pyproject.toml ./src/common_amirainvest_com/
COPY --chown=default:default ./src/common_amirainvest_com/lib/common_amirainvest_com/__init__.py \
./src/common_amirainvest_com/lib/common_amirainvest_com/

COPY --chown=default:default ./src/backend_amirainvest_com/pyproject.toml ./src/backend_amirainvest_com/
COPY --chown=default:default ./src/backend_amirainvest_com/lib/backend_amirainvest_com/__init__.py \
./src/backend_amirainvest_com/lib/backend_amirainvest_com/

ARG NO_DEV="-v"

RUN . $VIRTUALENV_PATH/bin/activate && poetry install --remove-untracked "$NO_DEV"

COPY --chown=default:default . .

ARG DEBUG="true"
ENV DEBUG=$DEBUG

ARG ENVIRONMENT="local"
ENV ENVIRONMENT=$ENVIRONMENT

ENV SQLALCHEMY_WARN_20=1

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]

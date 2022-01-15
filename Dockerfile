FROM python@sha256:dbbfcbf95f6b596d2be1d8f3b368016619f78f829facf6f2e361bea1151794e5 as base

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

COPY --chown=default:default ./src/brokerage_amirainvest_com/pyproject.toml ./src/brokerage_amirainvest_com/
COPY --chown=default:default ./src/brokerage_amirainvest_com/lib/brokerage_amirainvest_com/__init__.py \
./src/brokerage_amirainvest_com/lib/brokerage_amirainvest_com/

COPY --chown=default:default ./src/data_imports_amirainvest_com/pyproject.toml ./src/data_imports_amirainvest_com/
COPY --chown=default:default ./src/data_imports_amirainvest_com/lib/data_imports_amirainvest_com/__init__.py \
./src/data_imports_amirainvest_com/lib/data_imports_amirainvest_com/

COPY --chown=default:default ./src/market_data_amirainvest_com/pyproject.toml ./src/market_data_amirainvest_com/
COPY --chown=default:default ./src/market_data_amirainvest_com/lib/market_data_amirainvest_com/__init__.py \
./src/market_data_amirainvest_com/lib/market_data_amirainvest_com/


RUN . $VIRTUALENV_PATH/bin/activate && poetry install --remove-untracked --no-dev

ARG INSTALL_DEV_DEPS="true"
RUN if [ "$INSTALL_DEV_DEPS" = "true" ] ; then . $VIRTUALENV_PATH/bin/activate && poetry install --remove-untracked; fi


COPY --chown=default:default . .

ARG DEBUG="true"
ENV DEBUG=$DEBUG

ARG ENVIRONMENT="local"
ENV ENVIRONMENT=$ENVIRONMENT

ARG PROJECT="mono"
ENV PROJECT=$PROJECT

ENV SQLALCHEMY_WARN_20=1

EXPOSE 5000

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]

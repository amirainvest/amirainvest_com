# python:3.9-slim
FROM python@sha256:a9cf2d58b33ba6f273e80d1f6272186d8930c062fa2a2abc65f35bdf4609a032 as base

WORKDIR /opt

ARG USER_UID=1000
RUN adduser --shell /bin/sh --system --group --uid "${USER_UID}" default

RUN chown -R default /opt

USER default

ENV VIRTUALENV_PATH="/home/default/venv"
ENV PATH "/home/default/.local/bin:$PATH"
ENV PROJECT_NAME="backend_amirainvest_com"
ENV PROJECT="backend"
ENV AWS_DEFAULT_REGION="us-east-1"

EXPOSE 5000:5000

FROM base as builder

RUN python -m venv $VIRTUALENV_PATH
RUN pip install poetry

COPY --chown=default:default ./src/$PROJECT_NAME/poetry.lock ./src/$PROJECT_NAME/pyproject.toml ./src/$PROJECT_NAME/
COPY --chown=default:default ./src/$PROJECT_NAME/lib/$PROJECT_NAME/__init__.py \
./src/$PROJECT_NAME/lib/$PROJECT_NAME/

COPY --chown=default:default ./src/common_amirainvest_com/poetry.lock ./src/common_amirainvest_com/pyproject.toml \
./src/common_amirainvest_com/

COPY --chown=default:default ./src/common_amirainvest_com/lib/common_amirainvest_com/__init__.py \
./src/common_amirainvest_com/lib/common_amirainvest_com/

ARG NO_DEV="-v"
WORKDIR ./src/$PROJECT_NAME/

RUN . $VIRTUALENV_PATH/bin/activate && poetry install --remove-untracked --no-dev

ARG INSTALL_DEV_DEPS="true"
RUN if [ "$INSTALL_DEV_DEPS" = "true" ] ; then . $VIRTUALENV_PATH/bin/activate && poetry install --remove-untracked; fi

WORKDIR /opt

FROM base as final

COPY --chown=default:default ./src/$PROJECT_NAME/ ./src/$PROJECT_NAME/
COPY --chown=default:default ./src/common_amirainvest_com/ ./src/common_amirainvest_com/

COPY --chown=default:default --from=builder "$VIRTUALENV_PATH" "$VIRTUALENV_PATH"


ENTRYPOINT ["/bin/bash", "./src/backend_amirainvest_com/entrypoint.sh"]
CMD ["uvicorn", "backend_amirainvest_com.api.app:app", "--host", "0.0.0.0", "--port", "5000"]

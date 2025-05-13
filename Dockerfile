# Installation stage
FROM python:3.12-slim AS install

WORKDIR /fitness_app

ARG SERVER_PORT
ENV SERVER_PORT=${SERVER_PORT}

# Installing poetry
ENV POETRY_HOME=/opt/poetry
COPY install-poetry.py install-poetry.py
RUN python3 install-poetry.py --version 1.8.2

# Installing packages
COPY pyproject.toml poetry.lock ./
RUN $POETRY_HOME/bin/poetry install --no-root -n --no-cache


# Running stage
FROM install AS run

COPY ./fitness_app ./fitness_app

ENTRYPOINT [ "sh", "-c", "$POETRY_HOME/bin/poetry run uvicorn --host 0.0.0.0 --port $SERVER_PORT fitness_app.main:app" ]


# Debug stage
FROM install AS debug

RUN $POETRY_HOME/bin/poetry add debugpy

ENTRYPOINT [ "sh", "-c", "$POETRY_HOME/bin/poetry run python -m debugpy --wait-for-client --listen 0.0.0.0:5678 -m uvicorn --host 0.0.0.0 --port $SERVER_PORT --reload fitness_app.main:app" ]


# Dev stage
FROM install AS Dev

ENTRYPOINT [ "sh", "-c", "$POETRY_HOME/bin/poetry run uvicorn --host 0.0.0.0 --port $SERVER_PORT --reload fitness_app.main:app" ]


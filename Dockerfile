FROM python:3.14-bookworm AS builder

# renovate: datasource=pypi depName=poetry
ENV POETRY_VERSION=2.3.0

RUN pip install --upgrade pip && pip install poetry==$POETRY_VERSION

ENV POETRY_VIRTUALENVS_IN_PROJECT=1
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root --no-cache

FROM python:3.14-slim-bookworm

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY cleaner ./cleaner

USER nobody
ENTRYPOINT ["python", "-m", "cleaner.main"]

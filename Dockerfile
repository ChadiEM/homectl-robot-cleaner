FROM python:3.11-buster as builder

# renovate: datasource=pypi depName=poetry
ENV POETRY_VERSION=1.6.0

RUN pip install --upgrade pip && pip install poetry==$POETRY_VERSION

ENV POETRY_VIRTUALENVS_IN_PROJECT=1
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root --no-cache

FROM python:3.11-alpine

RUN apk --no-cache upgrade && apk --no-cache add tzdata

ENV VIRTUAL_ENV=/app/.venv
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY cleaner ./cleaner

USER nobody
ENTRYPOINT ["python", "-m", "cleaner.main"]
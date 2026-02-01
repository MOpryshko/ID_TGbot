FROM python:3.12-alpine

RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache \
    git \
    curl \
    gcc \
    python3-dev

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN update-ca-certificates
RUN pip install --no-cache-dir "poetry>=2.0,<3.0"
RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./
RUN poetry install --only main --no-interaction --no-ansi

COPY . .
CMD ["python", "-m", "main"]

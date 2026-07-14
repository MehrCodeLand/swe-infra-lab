# Self-contained image for the RabbitMQ / Celery / Redis examples.
#
# Build context is THIS folder (see docker-compose.yml), so the section is fully
# independent and can be built or deployed on its own. The scripts read their
# broker host from RABBITMQ_HOST / REDIS_HOST (default: localhost), which
# docker-compose sets to the bundled service names.
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY . .

# Default to the raw RabbitMQ consumer; compose overrides `command` per service.
CMD ["uv", "run", "python", "consumer.py"]

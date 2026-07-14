# Image for the OpenTelemetry tracing pipeline (publisher API, consumer, llm_worker).
#
# The build context is the REPOSITORY ROOT (see docker-compose.yml) so we can
# install the shared dependencies from the top-level pyproject.toml, then copy
# only the OTel service code into the image. Copying the OTel folder's *contents*
# into /app keeps the Python module paths flat and unchanged:
#   publisher.main  /  consumer.worker  /  llm_worker.worker  /  telemetry
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# Copy the OTel service code (contents of the OTel/ folder) into /app.
COPY OTel/ ./

# Sensible default; docker-compose overrides `command` per service.
CMD ["uv", "run", "uvicorn", "publisher.main:app", "--host", "0.0.0.0", "--port", "8000"]

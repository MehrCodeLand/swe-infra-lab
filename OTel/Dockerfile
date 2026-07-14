# Self-contained image for the OpenTelemetry tracing pipeline.
#
# Build context is THIS folder (see docker-compose.yml), so the section is fully
# independent — it can be built, shipped or deployed on its own with no files
# from the repo root. Module paths stay flat and unchanged:
#   publisher.main  /  consumer.worker  /  llm_worker.worker  /  telemetry
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# Copy the rest of the section's code.
COPY . .

# Sensible default; docker-compose overrides `command` per service.
CMD ["uv", "run", "uvicorn", "publisher.main:app", "--host", "0.0.0.0", "--port", "8000"]

# rabbit/ — Messaging & caching

RabbitMQ, Celery and Redis basics as small, independent scripts. This section is
fully self-contained (its own `pyproject.toml` / `uv.lock` / `Dockerfile`), so
it runs on its own with a single Docker command.

## Option A — Docker (recommended, nothing to install)

```bash
# starts RabbitMQ + Redis + the consumer + a Celery worker
docker compose -f rabbit/docker-compose.yml up --build
```

Then run the one-shot scripts against that stack from another terminal:

```bash
# publish the sample emails (emails.txt) → the consumer picks them up
docker compose -f rabbit/docker-compose.yml run --rm producer uv run python produce.py

# queue a Celery task → the celery_worker runs it
docker compose -f rabbit/docker-compose.yml run --rm producer uv run python run_task.py

# Redis cache-aside demo
docker compose -f rabbit/docker-compose.yml run --rm producer uv run python redis_cache.py
```

- RabbitMQ management UI: **http://localhost:15672** (`guest` / `guest`) — watch
  the queue fill and drain.

## Option B — Run scripts on your host

Start only the infra, then run scripts with [uv](https://github.com/astral-sh/uv):

```bash
docker compose -f rabbit/docker-compose.yml up -d rabbitmq redis
cd rabbit && uv sync            # once, creates the environment
```

```bash
# Raw RabbitMQ producer / consumer
uv run python consumer.py       # terminal 1 — waits for messages
uv run python produce.py        # terminal 2 — publishes emails.txt

# Celery async task queue
uv run celery -A tasks worker --loglevel=info   # terminal 1
uv run python run_task.py                        # terminal 2 — queues a task

# Redis cache-aside
uv run python redis_cache.py
```

All scripts read `RABBITMQ_HOST` / `REDIS_HOST` (default `localhost`), so the
same code works on the host and inside the containers.

## Files at a glance

| File | What it demonstrates |
|------|----------------------|
| `produce.py` | reads `emails.txt`, publishes one message per line to `email_queue` |
| `consumer.py` | consumes messages, "calls" an LLM, stores results in SQLite, acks |
| `celery_app.py` | the Celery app, wired to the Redis broker + result backend |
| `tasks.py` | defines `send_email`, a task that sleeps 5s to simulate slow work |
| `run_task.py` | calls `send_email.delay(...)` and prints the task id instantly |
| `redis_cache.py` | Redis cache-aside: slow `Cache MISS`, then instant `Cache HIT` |
| `config.py` | shared constants (`RABBITMQ_HOST`, `QUEUE_NAME`) |
| `emails.txt` | sample input for `produce.py` (edit to try your own) |

> Note: `consumer.py` posts to a placeholder LLM URL (`api.example.com`), so the
> HTTP call fails unless you swap in a real endpoint — that's expected; the point
> here is the RabbitMQ delivery/ack flow.

## Docker files

- `Dockerfile` / `docker-compose.yml` — **self-contained** (RabbitMQ + Redis +
  workers). **Use this.**
- `Dockerfile.local` / `docker-compose.local.yml` — maintainer variant that puts
  everything on an external `shared_net` network (so the OTel `*.local` stack can
  share the same broker). Requires `docker network create shared_net` first.

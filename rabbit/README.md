# rabbit/ — Messaging & caching

RabbitMQ, Celery and Redis basics as small, independent scripts. Each one is
meant to be run by hand so you can watch it work.

## 1. Start the infrastructure

All the scripts here connect to `localhost`. Bring up RabbitMQ + Redis first:

```bash
docker compose -f rabbit/docker-compose.yml up -d
```

- RabbitMQ management UI: **http://localhost:15672** (`guest` / `guest`)
- Redis: `localhost:6379`

> Install the Python deps once from the repo root with `uv sync`. All commands
> below use `uv run`, which uses that environment automatically.

## 2. The examples

Run each from the **repo root** unless noted.

### a) Raw RabbitMQ producer / consumer

A minimal publish → consume pipeline over a durable `email_queue`. The consumer
pretends to call an LLM for each email and stores the result in a local SQLite
file (`rabbit/responses.db`).

```bash
# terminal 1 — start the worker (waits for messages)
cd rabbit && uv run python consumer.py

# terminal 2 — publish the sample emails from emails.txt
cd rabbit && uv run python produce.py
```

| File | Role |
|------|------|
| `produce.py` | reads `emails.txt`, publishes one message per line to `email_queue` |
| `consumer.py` | consumes messages, "calls" an LLM, writes to SQLite, acks |
| `emails.txt` | sample input (edit it to try your own messages) |

> Note: `consumer.py` posts to a placeholder LLM URL (`api.example.com`), so the
> HTTP call will fail unless you swap in a real endpoint — that's expected; the
> point is the RabbitMQ delivery/ack flow. Watch the queue drain in the RabbitMQ
> management UI while it runs.

### b) Celery async task queue (Redis broker)

Celery lets you hand slow work to a background worker and return instantly.

```bash
# terminal 1 — start a Celery worker
cd rabbit && uv run celery -A tasks worker --loglevel=info

# terminal 2 — queue a task (returns immediately with a task id)
cd rabbit && uv run python run_task.py
```

| File | Role |
|------|------|
| `celery_app.py` | the Celery app, wired to the Redis broker + result backend |
| `tasks.py` | defines `send_email`, a task that sleeps 5s to simulate slow work |
| `run_task.py` | calls `send_email.delay(...)` and prints the task id right away |

You'll see the worker (terminal 1) pick up and run the task ~instantly after you
launch `run_task.py`.

### c) Redis cache-aside

Demonstrates the cache-aside pattern: first lookup misses and hits the "DB"
(a 2s sleep), the second is served from Redis instantly.

```bash
uv run python rabbit/redis_cache.py
```

Expected output: a `Cache MISS` (slow) followed by a `Cache HIT` (instant).

## Files at a glance

| File | What it demonstrates | Run with |
|------|----------------------|----------|
| `produce.py` + `consumer.py` | Raw RabbitMQ pub/sub with durable queue + ack | `uv run python consumer.py` / `produce.py` |
| `celery_app.py` + `tasks.py` + `run_task.py` | Celery async tasks over Redis | `uv run celery -A tasks worker` / `run_task.py` |
| `redis_cache.py` | Redis cache-aside | `uv run python rabbit/redis_cache.py` |
| `config.py` | shared constants (`RABBITMQ_HOST`, `QUEUE_NAME`) | imported by other scripts |

## Docker files

- `docker-compose.yml` — self-contained RabbitMQ + Redis. **Use this.**
- `docker-compose.local.yml` — maintainer variant that puts RabbitMQ + Redis on
  an external `shared_net` network (so the OTel `*.local` stack can share them).
  Requires `docker network create shared_net` first.

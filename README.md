# swe-infra-lab

A hands-on lab for exploring core **software-engineering infrastructure** —
message queues, async task processing, caching and distributed tracing —
through small, runnable examples you can spin up in minutes and *see* working
(a queue draining, a cache hit, a trace in Jaeger).

The goal isn't theory. Each folder is a minimal, working mock project you can
run locally, see real results, and understand *why* the concept matters.

## The two sides

The project is split into two self-contained folders:

| Folder | Topic | What you'll find |
|--------|-------|------------------|
| [`rabbit/`](rabbit/) | **Messaging & caching** — RabbitMQ, Celery, Redis | Publisher/consumer patterns, async task queues, cache-aside |
| [`OTel/`](OTel/) | **Observability** — OpenTelemetry + Jaeger | A distributed, traced email pipeline you watch end-to-end in the Jaeger UI |

Each folder has its **own README with the exact files and commands to run**, and
its own Docker setup. Start with whichever side you're curious about.

## Structure

```
swe-infra-lab/
├── rabbit/                    # RabbitMQ + Celery + Redis basics
│   ├── README.md
│   ├── produce.py             # publish emails to a RabbitMQ queue
│   ├── consumer.py            # consume + "call LLM" + store in SQLite
│   ├── celery_app.py          # Celery app (Redis broker/backend)
│   ├── tasks.py               # a slow Celery task
│   ├── run_task.py            # queue a Celery task and return instantly
│   ├── redis_cache.py         # cache-aside pattern with Redis
│   ├── config.py              # shared constants
│   ├── emails.txt             # sample input for produce.py
│   ├── docker-compose.yml         # self-contained rabbitmq + redis
│   └── docker-compose.local.yml   # maintainer variant (external shared_net)
│
├── OTel/                      # OpenTelemetry distributed tracing
│   ├── README.md
│   ├── telemetry.py           # OTel/Jaeger setup helper
│   ├── bakery.py              # standalone nested-span demo
│   ├── load_test.py           # fire N requests at the pipeline
│   ├── publisher/main.py      # FastAPI API → RabbitMQ (traced)
│   ├── consumer/worker.py     # consume → forward (trace context propagated)
│   ├── llm_worker/worker.py   # final "classification" step (traced)
│   ├── Dockerfile / Dockerfile.local
│   ├── docker-compose.yml         # self-contained pipeline + rabbitmq + jaeger
│   └── docker-compose.local.yml   # maintainer variant (external shared_net)
│
├── pyproject.toml             # shared Python dependencies (uv)
└── uv.lock
```

## Quickstart

### Observability side (recommended first — nothing to run by hand)

```bash
docker compose -f OTel/docker-compose.yml up --build
uv run python OTel/load_test.py          # send 50 requests
```

Open the Jaeger UI at **http://localhost:16686** and look at the traces for the
`publisher` service — you'll see a single request flow across three services.
Full walkthrough: [`OTel/README.md`](OTel/README.md).

### Messaging side

```bash
docker compose -f rabbit/docker-compose.yml up -d   # start rabbitmq + redis
uv run python rabbit/redis_cache.py                 # try the cache demo
```

Full walkthrough (RabbitMQ producer/consumer + Celery): [`rabbit/README.md`](rabbit/README.md).

## `.local` vs default Docker files

Every Docker setup comes in two flavours:

* **`docker-compose.yml`** — **self-contained**. It bundles every dependency
  (RabbitMQ, Redis, Jaeger) so a new user can `docker compose up` and everything
  just works. **Use this one.**
* **`docker-compose.local.yml`** — the maintainer's variant. It expects
  RabbitMQ/Redis/Jaeger to already be running on an external `shared_net`
  network (started from a separate infra stack). Handy if you run shared infra
  once and point multiple projects at it.

## Requirements

- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv) for Python dependency management
  (`uv sync` once to create the environment; the `uv run …` commands above use it)

# swe-infra-lab

A hands-on lab for exploring core **software-engineering infrastructure** —
message queues, async task processing, caching and distributed tracing —
through small, runnable examples you can spin up in minutes and *see* working
(a queue draining, a cache hit, a trace in Jaeger).

The goal isn't theory. Each section is a minimal, working mock project you can
run locally, see real results, and understand *why* the concept matters.

## How this repo is organized

Every topic lives in its **own self-contained folder** — its own dependencies
(`pyproject.toml` + `uv.lock`), its own `Dockerfile`, and its own
`docker-compose.yml`. Nothing is shared at the root, so each section can be
built, run, uploaded or deployed **completely on its own**, and adding a new
section later (DevOps, Data Engineering, …) is just: copy the folder pattern.

| Folder | Topic | What you'll find |
|--------|-------|------------------|
| [`rabbit/`](rabbit/) | **Messaging & caching** — RabbitMQ, Celery, Redis | Publisher/consumer, async task queues, cache-aside |
| [`OTel/`](OTel/) | **Observability** — OpenTelemetry + Jaeger | A distributed, traced email pipeline you watch end-to-end in the Jaeger UI |
| _(planned)_ | DevOps, Data Engineering, … | Each will follow the same self-contained pattern |

Each folder has its **own README with the exact files and commands to run**.

## Structure

```
swe-infra-lab/
├── rabbit/                    # ── self-contained section ──
│   ├── README.md
│   ├── pyproject.toml / uv.lock       # section dependencies
│   ├── Dockerfile / Dockerfile.local
│   ├── docker-compose.yml             # self-contained: rabbitmq + redis + workers
│   ├── docker-compose.local.yml       # maintainer variant (external shared_net)
│   ├── produce.py / consumer.py       # raw RabbitMQ pub/sub
│   ├── celery_app.py / tasks.py / run_task.py   # Celery async tasks
│   ├── redis_cache.py                 # cache-aside with Redis
│   ├── config.py / emails.txt
│
├── OTel/                      # ── self-contained section ──
│   ├── README.md
│   ├── pyproject.toml / uv.lock
│   ├── Dockerfile / Dockerfile.local
│   ├── docker-compose.yml             # self-contained: pipeline + rabbitmq + jaeger
│   ├── docker-compose.local.yml       # maintainer variant (external shared_net)
│   ├── telemetry.py / bakery.py / load_test.py
│   ├── publisher/main.py              # FastAPI API → RabbitMQ (traced)
│   ├── consumer/worker.py             # consume → forward (trace context propagated)
│   └── llm_worker/worker.py           # final "classification" step (traced)
│
└── README.md                 # you are here
```

## Quickstart

Each section runs with one Docker command — no host Python setup needed.

**Observability (recommended first):**

```bash
docker compose -f OTel/docker-compose.yml up --build
# then, in another terminal, send traffic:
docker compose -f OTel/docker-compose.yml run --rm \
  -e TARGET_URL=http://publisher:8000 publisher uv run python load_test.py
```

Open **http://localhost:16686** (Jaeger) and inspect traces for the `publisher`
service. Full walkthrough: [`OTel/README.md`](OTel/README.md).

**Messaging:**

```bash
docker compose -f rabbit/docker-compose.yml up --build
# publish the sample emails:
docker compose -f rabbit/docker-compose.yml run --rm producer uv run python produce.py
```

Full walkthrough: [`rabbit/README.md`](rabbit/README.md).

> Prefer running scripts directly on your machine? Every section also works with
> [uv](https://github.com/astral-sh/uv): `cd <section> && uv sync`, start the
> infra with `docker compose … up -d`, then `uv run python <script>.py`. See
> each section's README.

## The two Docker flavours

Every section ships two compose files:

* **`docker-compose.yml`** — **self-contained**. Bundles every dependency
  (RabbitMQ / Redis / Jaeger) so a new user can `docker compose up --build` and
  everything just works. **Use this one.**
* **`docker-compose.local.yml`** — maintainer variant. Expects the infra to
  already run on an external `shared_net` network (`docker network create
  shared_net`), so multiple sections can share one broker/tracing backend.

## Requirements

- Docker & Docker Compose (that's all you need for the quickstarts)
- Optional: [uv](https://github.com/astral-sh/uv), only if you want to run the
  Python scripts directly on your host instead of in containers

# OTel/ — Distributed tracing with OpenTelemetry + Jaeger

A traced email-processing pipeline. One HTTP request flows through **three
services** over RabbitMQ, and OpenTelemetry stitches the whole journey into a
single trace you can inspect in the **Jaeger UI**.

```
POST /send-email ──► publisher ──(emails)──► consumer ──(classification_results)──► llm_worker
      (FastAPI)                                                                     (fake LLM)
   every hop carries the trace context, so it shows up as ONE trace in Jaeger
```

## Run the full pipeline (self-contained)

Nothing to run by hand — RabbitMQ, Jaeger and all three services are bundled:

```bash
docker compose -f OTel/docker-compose.yml up --build
```

Then, from another terminal, send some traffic and open the UI:

```bash
# runs load_test.py inside a throwaway container against the running stack
docker compose -f OTel/docker-compose.yml run --rm \
  -e TARGET_URL=http://publisher:8000 publisher uv run python load_test.py
```

(Or, on your host: `curl -X POST "http://localhost:8000/send-email?subject=hello"`.)

- **Jaeger UI:** http://localhost:16686 — pick service **`publisher`**, click
  *Find Traces*, open one and expand it. You'll see spans for
  `publish_to_rabbitmq` → `process_email` → `db_lookup_sender_history` →
  `llm_classification`, across the three services.
- **RabbitMQ management UI:** http://localhost:15672 (`guest` / `guest`)
- **Publisher API:** http://localhost:8000 — e.g.
  `curl -X POST "http://localhost:8000/send-email?subject=hello"`

Some `llm_classification` spans are tagged `llm.slow=true` (random latency > 1s)
— a good way to see how tracing surfaces bottlenecks.

## Files at a glance

| File | Role | Run with |
|------|------|----------|
| `publisher/main.py` | FastAPI endpoint `/send-email`, publishes to RabbitMQ, starts the trace | (container) `uvicorn publisher.main:app` |
| `consumer/worker.py` | consumes `emails`, forwards to `classification_results`, propagates context | (container) `python -m consumer.worker` |
| `llm_worker/worker.py` | final "classification" step with simulated LLM latency | (container) `python -m llm_worker.worker` |
| `telemetry.py` | shared helper: wires OTel up to the Jaeger OTLP endpoint | imported by the services |
| `load_test.py` | sends N concurrent requests to the running pipeline | see command above |
| `bakery.py` | standalone tracing demo — no RabbitMQ needed (see below) | `cd OTel && uv run python bakery.py` |

## Standalone demo: `bakery.py`

If you just want to understand **spans and parent/child nesting** without the
whole pipeline, `bakery.py` traces a fake "make a cake" workflow in a single
process. It exports to a Jaeger running on `localhost:4317`, so start Jaeger
first (the compose above exposes that port), then run it on your host:

```bash
cd OTel && uv sync && uv run python bakery.py
```

Open http://localhost:16686 and look at the **`bakery`** service — you'll see
`make_cake` as the parent span wrapping `gather_ingredients`, `mix_batter`,
`bake_cake` and `decorate_cake`.

## Docker files

This section is fully self-contained: its own `pyproject.toml` / `uv.lock` and a
build context of this folder, so it can be built or deployed on its own.

- `Dockerfile` / `docker-compose.yml` — **self-contained**. Bundles RabbitMQ +
  Jaeger + the three services. **Use this.**
- `Dockerfile.local` / `docker-compose.local.yml` — maintainer variant. Expects
  RabbitMQ (and Redis) to already exist on an external `shared_net` network:

  ```bash
  docker network create shared_net
  docker compose -f OTel/docker-compose.local.yml up --build
  ```

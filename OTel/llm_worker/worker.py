import json, pika, os, random, time
from opentelemetry.propagate import extract
from opentelemetry import context
from telemetry import setup_telemetry

tracer = setup_telemetry("llm_worker")

def callback(ch, method, properties, body):
    headers = properties.headers or {}
    ctx = extract(headers)
    token = context.attach(ctx)

    try:
        with tracer.start_as_current_span("llm_classification") as span:
            data = json.loads(body)
            span.set_attribute("email.subject", data["subject"])

            # simulate variable LLM latency (this is where real bottlenecks live)
            delay = random.uniform(0.1, 1.2)
            time.sleep(delay)
            span.set_attribute("llm.latency_seconds", delay)
            span.set_attribute("llm.model", "fake-gpt")

            if delay > 1.0:
                span.set_attribute("llm.slow", True)
    finally:
        context.detach(token)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ["RABBITMQ_HOST"]))
    channel = conn.channel()
    channel.queue_declare(queue="classification_results")
    channel.basic_consume(queue="classification_results", on_message_callback=callback)
    print("llm_worker waiting...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
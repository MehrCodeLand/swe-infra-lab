import json, pika, os, random, time
from opentelemetry.propagate import extract, inject
from opentelemetry import context
from telemetry import setup_telemetry

tracer = setup_telemetry("consumer")

def get_channel():
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ["RABBITMQ_HOST"]))
    ch = conn.channel()
    ch.queue_declare(queue="emails")
    ch.queue_declare(queue="classification_results")
    return conn, ch

def callback(ch, method, properties, body):
    headers = properties.headers or {}
    ctx = extract(headers)
    token = context.attach(ctx)

    try:
        with tracer.start_as_current_span("process_email") as span:
            data = json.loads(body)
            span.set_attribute("email.subject", data["subject"])

            with tracer.start_as_current_span("db_lookup_sender_history"):
                time.sleep(random.uniform(0.01, 0.05))  # simulate DB variance

            # forward to llm_worker service, propagate trace context
            out_headers = {}
            inject(out_headers)
            conn2, ch2 = get_channel()
            ch2.basic_publish(
                exchange="", routing_key="classification_results",
                body=json.dumps(data),
                properties=pika.BasicProperties(headers=out_headers),
            )
            conn2.close()
    finally:
        context.detach(token)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ["RABBITMQ_HOST"]))
    channel = conn.channel()
    channel.queue_declare(queue="emails")
    channel.basic_consume(queue="emails", on_message_callback=callback)
    print("consumer waiting...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
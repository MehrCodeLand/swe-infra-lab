import json
import pika
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagate import inject
from telemetry import setup_telemetry
import os

tracer = setup_telemetry("publisher")

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

def get_channel():
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ["RABBITMQ_HOST"]))
    channel = conn.channel()
    channel.queue_declare(queue="emails")
    return conn, channel

@app.post("/send-email")
def send_email(subject: str):
    with tracer.start_as_current_span("publish_to_rabbitmq") as span:
        span.set_attribute("email.subject", subject)

        headers = {}
        inject(headers)  # injects current trace context into headers

        conn, channel = get_channel()
        channel.basic_publish(
            exchange="",
            routing_key="emails",
            body=json.dumps({"subject": subject}),
            properties=pika.BasicProperties(headers=headers),
        )
        conn.close()

    return {"status": "queued", "subject": subject}
import os
import pika
import json

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

def read_emails(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    return [{"id": i, "content": line.strip()} for i, line in enumerate(lines) if line.strip()]

def publish_emails(emails):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='email_queue', durable=True)

    for email in emails:
        channel.basic_publish(
            exchange='',
            routing_key='email_queue',
            body=json.dumps(email),
            properties=pika.BasicProperties(delivery_mode=2)  # persist message
        )
        print(f"Published email {email['id']}")

    connection.close()

if __name__ == "__main__":
    emails = read_emails("emails.txt")
    publish_emails(emails)
    print(f"Done. Published {len(emails)} emails.")
import os
import pika
import json
import requests
import sqlite3  # simple local DB for this example — swap for Postgres later

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

# --- Simple DB setup ---
conn = sqlite3.connect("responses.db", check_same_thread=False)
conn.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY,
        email_content TEXT,
        llm_response TEXT
    )
""")
conn.commit()

def call_llm(content):
    # Replace with your real LLM API call
    response = requests.post(
        "https://api.example.com/generate",
        json={"prompt": content}
    )
    return response.json().get("text", "")

def store_response(email_id, content, response):
    conn.execute(
        "INSERT OR REPLACE INTO responses (id, email_content, llm_response) VALUES (?, ?, ?)",
        (email_id, content, response)
    )
    conn.commit()

def callback(ch, method, properties, body):
    email = json.loads(body)
    print(f"Processing email {email['id']}...")

    llm_response = call_llm(email["content"])
    store_response(email["id"], email["content"], llm_response)

    print(f"Stored response for email {email['id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='email_queue', durable=True)
    channel.basic_qos(prefetch_count=10)  # process one at a time (safe default)

    channel.basic_consume(queue='email_queue', on_message_callback=callback)
    print("Worker started. Waiting for emails...")
    channel.start_consuming()
  
if __name__ == "__main__":
    main()
import os
from celery import Celery

# Host defaults to localhost (running scripts on your machine) but can be
# overridden with REDIS_HOST when running inside Docker.
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_URL = f"redis://{REDIS_HOST}:6379/0"

app = Celery(
    'tasks',
    broker=REDIS_URL,    # where tasks are queued
    backend=REDIS_URL,   # where results are stored
)

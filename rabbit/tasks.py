from celery_app import app
import time

@app.task
def send_email(user_email):
    print(f"Sending email to {user_email}...")
    time.sleep(5)  # simulate slow work
    print("Email sent!")
    return f"Email sent to {user_email}"
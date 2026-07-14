from tasks import send_email

# This returns INSTANTLY — doesn't block waiting for the 5 seconds
result = send_email.delay("mehrshad@example.com")

print("Task queued! ID:", result.id)

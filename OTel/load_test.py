import asyncio, httpx, random, os

SUBJECTS = ["invoice", "meeting request", "spam offer", "password reset", "newsletter"]

# On the host the publisher is reachable at localhost:8000; inside the compose
# network use TARGET_URL=http://publisher:8000.
BASE_URL = os.getenv("TARGET_URL", "http://localhost:8000")

async def fire(client, i):
    subject = f"{random.choice(SUBJECTS)}-{i}"
    r = await client.post(f"{BASE_URL}/send-email", params={"subject": subject})
    print(i, r.status_code)

async def main(n=50):
    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[fire(client, i) for i in range(n)])

if __name__ == "__main__":
    asyncio.run(main())
import asyncio, httpx, random

SUBJECTS = ["invoice", "meeting request", "spam offer", "password reset", "newsletter"]

async def fire(client, i):
    subject = f"{random.choice(SUBJECTS)}-{i}"
    r = await client.post("http://localhost:8000/send-email", params={"subject": subject})
    print(i, r.status_code)

async def main(n=50):
    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[fire(client, i) for i in range(n)])

if __name__ == "__main__":
    asyncio.run(main())
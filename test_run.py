import asyncio
import aiohttp
import time
import sys

async def fetch(session, i):
    print(f"🚀 Request {i} sent...", flush=True) 
    start = time.time()
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with session.get("http://127.0.0.1:8000/api/stock/AAPL", timeout=timeout) as response:
            status = response.status
            await response.text()
            print(f"✅ Request {i} finished with status {status} in {time.time() - start:.2f} seconds", flush=True)
    except Exception as e:
        print(f"❌ Request {i} failed: {e}", flush=True)

async def main():
    print("🎬 Starting load test inside event loop...", flush=True)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, i) for i in range(10)]
        await asyncio.gather(*tasks)

# מוחקים את ה-if __name__ ואת הבדיקות הגרנדיוזיות ומריצים ישירות בשורש הקובץ!
print("🏁 Script started execution directly...", flush=True)

if sys.platform == 'win32':
    print("🛠️ Applying Windows event loop policy...", flush=True)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
print("🚀 Invoking asyncio.run...", flush=True)
asyncio.run(main())
print("🏁 Script finished completely.", flush=True)
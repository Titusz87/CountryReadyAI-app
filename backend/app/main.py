from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from app.poll_dataquoll import poll_dataquoll 


latest_warnings = [] # !! swap for db later

scheduler = AsyncIOScheduler()

async def run_poll():
    global latest_warnings
    latest_warnings = await poll_dataquoll()

@asynccontextmanager         
async def lifespan(app: FastAPI):   # Reference: https://fastapi.tiangolo.com/advanced/events/#lifespan
    await run_poll()                # populates immediately on boot
    scheduler.add_job(run_poll, "interval", minutes=2)
    scheduler.start()

    yield   # app runs while paused here

    # shutdown logic
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"warnings": latest_warnings}
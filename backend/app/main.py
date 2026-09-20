from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.poll_dataquoll import poll_dataquoll 

app = FastAPI()


@app.get("/")
async def root():
    response = await poll_dataquoll()
    return {"message": response}
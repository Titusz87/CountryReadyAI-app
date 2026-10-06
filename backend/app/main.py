from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.poll_dataquoll import poll_all_states

app = FastAPI()

@app.get("/")
async def root():
    #response = await poll_dataquoll_by_state()
    response = await poll_all_states()
    return {"message": response}
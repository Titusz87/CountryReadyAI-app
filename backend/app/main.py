from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.poll_dataquoll import poll_all_states, setup_polling

#this code runs when the server is created 
#'asynccontextmanager' decorator makes 'lifespan' fn work as a context manager  
@asynccontextmanager
async def lifespan(app: FastAPI):
    #one time setup stuff runs here 
    setup_polling()
    await poll_all_states() #poll immediately on startup for testing
    #setup db 
    #setup anything else
    
    #create scheduler and set it to automatically poll every 2 minutes 
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        poll_all_states,
        "interval",
        minutes=2
    )
    scheduler.start()
    yield
    scheduler.shutdown()

#fastAPI runs with 'lifespan' fn
app = FastAPI(lifespan=lifespan)

#the root of the API
@app.get("/")
async def root():
    return {"message": "g'day"}

#use this to test functionalities 
@app.get("/test")
async def root():
    return {"message": "test"}


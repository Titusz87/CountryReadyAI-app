from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.poll_dataquoll import poll_all_states, setup_polling
from app.database import connect_to_db, get_session
from app.poll_dataquoll import auto_poll_interval
#all the routes here
from app.routers.registration import router as registration_router
#from app.routers.something_else import router as something_else

poll = False

#this code runs when the server is created 
#'asynccontextmanager' decorator makes 'lifespan' fn work as a context manager  
@asynccontextmanager
async def lifespan(app: FastAPI):
    #one time setup stuff runs here 
    connect_to_db()
    setup_polling()
    if poll:
        await poll_all_states() #poll immediately on startup for testing
    run_db_tests()
    #setup anything else here
    
    #create scheduler and set it to automatically poll every 2 minutes 
    scheduler = AsyncIOScheduler()
    if poll:
        scheduler.add_job(
            poll_all_states,
            "interval",
            minutes=auto_poll_interval
        )
    scheduler.start()
    yield
    scheduler.shutdown()

#fastAPI runs with 'lifespan' fn. add routers
app = FastAPI(lifespan=lifespan)
app.include_router(registration_router)
#app.include_router(something_else_router)

#the root of the API
@app.get("/")
def root():
    return {"message": "Hello from CountryReady!"}

#can do database stuff here
def run_db_tests():
    with get_session() as session:
        pass


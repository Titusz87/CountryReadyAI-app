from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.poll_dataquoll import poll_all_states, setup_polling
from app.firebase import initialise_firebase, firebase_test_notification
from app.database import connect_to_db, get_session
from app.routers.registration import router as registration_router
#from app.routers.something_else import router as something_else
from app.services import db_helpers as db
from app import models

#--------------control vars------------------------------------------

auto_poll = False
poll_on_startup = False
auto_poll_interval = 2
flush_db_models = [models.People]
test_firebase_notification_system = False


#------------------------------------------------------------------

#this code runs when the server is created 
#'asynccontextmanager' decorator makes 'lifespan' fn work as a context manager  
@asynccontextmanager
async def lifespan(app: FastAPI):
    #one time setup stuff runs here 
    load_dotenv(".env")
    initialise_firebase()
    connect_to_db()
    setup_polling()
    if poll_on_startup:
        await poll_all_states() #poll immediately on startup for testing
    do_additional_db_jobs()
    do_additional_firebase_jobs()
    
    #create scheduler and set it to automatically poll every 2 minutes 
    scheduler = AsyncIOScheduler()
    if auto_poll:
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
def do_additional_db_jobs():
    with get_session() as session:
        
        if not flush_db_models:
            for model in flush_db_models:
                db.flush_db_table(session, model)
                db.print_table_info(session, model)
        session.commit()

def do_additional_firebase_jobs():
    if test_firebase_notification_system:
        firebase_test_notification()
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.models import Base

DATABASE_URL = None
engine = None 
SessionLocal = None

#create url that the app will use to connect to the db
def connect_to_db():
    #access .env values to create url
    load_dotenv(".env")   
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')

    if not (DB_USER and DB_PASSWORD and DB_NAME):
        raise RuntimeError("DB_USER and DB_PASSWORD and DB_NAME are not set in .env")
    
    #create url with env vars- to connect to db
    global DATABASE_URL
    DATABASE_URL = (
        f"postgresql+psycopg://"
        f"{DB_USER}:{DB_PASSWORD}"
        f"@localhost:5432/{DB_NAME}"
    )

    #create engine to be used for sessions 
    global engine 
    engine = create_engine(DATABASE_URL)

    #create all tables if they don't exit
    Base.metadata.create_all(engine)

    global SessionLocal
    SessionLocal = sessionmaker(bind=engine)

    print("Successfully connected to database")

#this is called by table classes when they do db fn's 
def get_session():
    if not engine:
        raise RuntimeError("Engine not created before session started")
    return SessionLocal()

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session

#DeclarativeBase is an sqlalchemy class the we inherit from to create our table classes 
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    age: Mapped[int | None]


# create url that the app will use to connect to the db
# access .env values to create url
load_dotenv(".env")
DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
    f"@localhost:5432/{os.environ['DB_NAME']}"
)

#use sqalchemy to create engine and create session 
engine = create_engine(DATABASE_URL)
with Session(engine) as session:
    user = User(name="Evan", email="evan@example.com")
    session.add(user)
    session.commit()


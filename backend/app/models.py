from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

#--------------table classes (define how to read and write objects to db)------------------------------

#DeclarativeBase is an sqlalchemy class the we inherit from to create our table classes 
class Base(DeclarativeBase):
    pass

#stores the info of current incidents 
class Current_Incident(Base):
    __tablename__ = "current_incidents"
    id: Mapped[str] = mapped_column(primary_key=True)
    event_type: Mapped[str]
    status: Mapped[str]
    warning_level: Mapped[str]
    state: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    last_updated: Mapped[str]
    reported_time: Mapped[str | None] #these values may be blank
    expires: Mapped[str | None]
    description: Mapped[str | None]
    address: Mapped[str | None]

#stores info of community leaders  
class Community_Leader(Base):
    __tablename__ = "community_leaders"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    latitude: Mapped[float] 
    longitude: Mapped[float] 

#this table store the community info that is created by community leaders
class Community_Profile(Base):
    __tablename__ = "community_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)

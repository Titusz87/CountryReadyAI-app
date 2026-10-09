from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime 
from sqlalchemy import DateTime

#--------------table classes (define how to read and write objects to db)------------------------------

#DeclarativeBase is an sqlalchemy class the we inherit from to create our table classes 
class Base(DeclarativeBase):
    pass

#stores the info of current incidents 
class Incident(Base):
    __abstract__ = True #this class to be inherited 

    id: Mapped[str] = mapped_column(primary_key=True)
    event_type: Mapped[str]
    status: Mapped[str]
    warning_level: Mapped[str]
    state: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    last_updated: Mapped[datetime] #dataquoll provides timezone-aware ISO 8601 timestamps for time values
    reported_time: Mapped[datetime | None] #these values may be blank
    expires: Mapped[datetime | None]       #datetime values might need to be converted to timezone values
    description: Mapped[str | None]
    address: Mapped[str | None]

#these 3 tables inherit from the incident class
#Current_Incident stores the incidents that are in progress
class Current_Incident(Incident):
    __tablename__ = "current_incidents"
#keep incidents that are no longer active for our records
class Archived_Incident(Incident):
    __tablename__ = "archived_incidents"
#this one is handy
class Temporary_Incident(Incident):
    __tablename__ = "temporary_incidents"

#stores info of community leaders  
class Community_Leader(Base):
    __tablename__ = "community_leaders"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    latitude: Mapped[float] 
    longitude: Mapped[float] 

#stores info of individual households (users)
class Household(Base):
    __tablename__ = "households"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    latitude: Mapped[float] 
    longitude: Mapped[float] 

#this table store the community info that is created by community leaders
class Community_Profile(Base):
    __tablename__ = "community_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)

#we need to remember which incidents affect which people
class Affected_Households(Base):
    __tablename__ = "affected_households"
    id: Mapped[int] = mapped_column(primary_key=True) #this is the same as the primary key for households
    incidents: Mapped[str]                            #this string can store the id's of incidents

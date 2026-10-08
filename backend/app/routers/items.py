from app import models
from app.database import get_session
from sqlalchemy.orm import Session
from sqlalchemy import delete
from sqlalchemy import select

verbose_debug = True
testing_mode = False 
possible_statuses = ['completed', 'safe', 'active', 'controlled', 'contained']
possible_warning_levels = ['advice', 'none', 'watch_and_act']

#----------basic read write logic-------------------------------------

#postgresql can insert any mixed list of table objects into db easily
def write_list_to_db(session, objects):
    try:
        session.add_all(objects)  
        if verbose_debug:
            print(f"Added {len(objects)} objects to db session")
    except Exception as e:
        print(f"Failed to write objects to db: {e}")

#delete row by inputting a table_object list 
def delete_db_rows(session, rows):
    try:
        for row in rows:
            session.delete(row)

        if verbose_debug:
            print(f"Prepared {len(rows)} rows to be deleted")
    except Exception as e:
        print(f"Failed to delete rows from db: {e}")

#reading is the opposite process 
def get_table(session, table_object):
    try:
        result = session.execute(select(table_object))
        return result.scalars().all()                     #scalars turns row into objects. Returned objects are detached when session closes 
    except Exception as e:
        print(f"Failed to get table from db: {e}")

#get rows by filtering a table by it's fields 
#input a dictionary of field -> field value (key -> value)
def get_db_rows_by_fields(session, table_object, fields):
    try:
        query = select(table_object)
        for field, value in fields.items():
            query = query.where(getattr(table_object, field) == value) #narrows down the list of table objects every time it runs 
        rows = session.execute(query).scalars().all()

        if verbose_debug:
            print(f"Selected {len(query)} rows from {table_object.__name__} table where {fields}")
        return rows
    except Exception as e:
        print(f"Failed to retrieve db rows based on fields")

#takes a list of objects and updates their various tables
#may not need this
# def update_db_rows(session, rows):
#     try:
#         for row in rows:
#             #session.merge(row)
#         print(f"Successfully updated {len(rows)} rows in db tables")
#     except Exception as e:
#         print(f"Failed to update rows in db: {e}")

#return all the id's from a table
def get_ids(session, table_object):
    try:
        result = session.execute(select(table_object.id))
        return result.scalars().all()
    except Exception as e:
        print(f"Failed to get id's from table {table_object.__name__}: {e}")

#wipe all the rows from a table
def flush_db_table(session, table_object):
    try:
        session.execute(delete(table_object))

        if verbose_debug:
            print(f"Prepared all rows from {table_object.__name__} to be deleted")
    except Exception as e:
        print(f"Failed to flush db table: {e}")

#return any wanted info about tables for debugging
def get_table_info(session, table_object):
    try:
        current_incidents = get_table(session, table_object)
        print(f"Size of {table_object.__name__} table: {len(current_incidents)}")
    except Exception as e:
        print(f"Failed to get table info: {e}")

#a flexible fn to use for testing stuff 
def run_db_tests():
    if testing_mode:
        with get_session() as session:
            #get_table(session, models.Current_Incident)
            
            get_table_info(session, models.Current_Incident)
            
        
#-----------specific jobs-------------------------------------

#this fn is called from the polling script
def update_database_incidents(incidents):
    #need to turn our incidents class into proper table objects before writing them to db
    current_incidents = translate_incident_objects_to_table_objects(incidents)

    with get_session() as session:
        #new incidents need to be checked against old ones to ensure the same object isn't inserted into the db twice
        #TODO
        common_ids = set()
        new_incident_ids = [incident.id for incident in incidents]
        previous_incident_ids = get_ids(session, models.Current_Incident)
        
        #the new incidents are safely written to the db
        #if new incident has been updated, the record needs to also be updated 
        
        #the incidents that have status changes are moved to archived incidents 

        #print(f"size of previous incident_ids: {len(previous_incident_ids)}")
        #print(f"size of new incidents ids: {len(new_incident_ids)}")
      
    #if the status has changed or the incident has expired, remove it from current and put it in archived    
    
        #write_list_to_db(session, current_incidents)
        session.commit()

#convert incidents between our python class and table class 
def translate_incident_objects_to_table_objects(incidents):
    translated = []
    for incident in incidents:
        current_incident = models.Current_Incident(
            id = incident.id,
            event_type = incident.event_type,
            status = incident.status, 
            warning_level = incident.warning_level, 
            state = incident.state,
            latitude = incident.latitude, 
            longitude = incident.longitude, 
            reported_time = incident.reported_time,
            last_updated = incident.last_updated,
            expires = incident.expires,
            description = incident.description, 
            address = incident.address
        )
        translated.append(current_incident)
    return translated

#create row in household table
def create_household():
    #TODO
    #generate an id. receive data from client
    pass
 
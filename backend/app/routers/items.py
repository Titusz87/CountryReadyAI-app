from app import models
from app.database import get_session
from sqlalchemy.orm import Session
from sqlalchemy import delete
from sqlalchemy import select

verbose_debug = False
monitor_incident_tables = True
testing_mode = False 

#----------basic read write logic-------------------------------------
#convert incidents between our python class and table class after polling
def convert_incidents_orm_objects(incidents, incident_type):
    translated = []
    for incident in incidents:
        current_incident = incident_type(
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
def get_all_rows(session, model):
    try:
        result = session.execute(select(model))
        return result.scalars().all()                     #scalars turns row into objects. Returned objects are detached when session closes 
    except Exception as e:
        print(f"Failed to get table from db: {e}")

#get rows by filtering a table by it's fields 
#input a dictionary of 'field -> value' ie 'key -> value'
def get_db_rows_by_fields(session, model, fields):
    try:
        query = select(model)
        for field, value in fields.items():
            query = query.where(getattr(model, field) == value) #narrows down the list of table objects every time it runs 
        rows = session.execute(query).scalars().all()

        if verbose_debug:
            print(f"Selected {len(query)} rows from {model.__tablename__} table where {fields}")
        return rows
    except Exception as e:
        print(f"Failed to retrieve db rows based on fields")

#return all the id's from a table
def get_ids_from_table(session, model):
    try:
        result = session.execute(select(model.id)) #id is always the primary key in our tables
        return result.scalars().all()
    except Exception as e:
        print(f"Failed to get ids from table {model.__tablename__}: {e}")

#sort of the opposite of 'get_ids'
def get_rows_from_ids(session, model, ids):
    try:
        result = session.execute(select(model).where(model.id.in_(ids))) 
        return result.scalars().all()
    except Exception as e:
        print(f"Failed to get the rows from table {model.__tablename__} by their ids: {e}")

#wipe all the rows from a table
def flush_db_table(session, model):
    try:
        session.execute(delete(model))

        if verbose_debug:
            print(f"Prepared all rows from {model.__tablename__} to be deleted")
    except Exception as e:
        print(f"Failed to flush db table: {e}")

#return any wanted info about tables for debugging
def get_table_info(session, model):
    try:
        current_incidents = get_all_rows(session, model)
        print(f"Size of {model.__tablename__} table: {len(current_incidents)}")
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
#this is complicated. Please don't touch it!
def update_database_incidents(incidents):
    print("Updating current incidents...")
    
    #need to turn our incidents class into proper table objects before writing them to db
    #we need to compare the ids of things because they are unique (objects may not be)
    new_incidents = convert_incidents_orm_objects(incidents, models.Temporary_Incident) #these are 'Temporary_Incidents(s)'
    new_incident_ids = [incident.id for incident in new_incidents] 
    
    with get_session() as session:
        #we need to store the new incidents in a temporary table for logic later (the temporary_incidents is empty)
        write_list_to_db(session, new_incidents)           #writes to temporary_incidents
        print(f"Added {len(new_incidents)} new incidents to {models.Temporary_Incident.__tablename__}")

        if monitor_incident_tables:
            get_table_info(session, models.Temporary_Incident)
            get_table_info(session, models.Current_Incident)
            get_table_info(session, models.Archived_Incident)
        
        #get the previous incidents and their ids 
        previous_incidents = get_all_rows(session, models.Current_Incident)
        previous_incident_ids = get_ids_from_table(session, models.Current_Incident)
        
        #incidents ids that are in common can't be inserted into 'current_incidents'because they already exist
        #they need to be checked to see if the incidents have updated  
        common_incidents_ids = set(new_incident_ids) & set(previous_incident_ids) #only sets have special operations like '&' and '-' (because they don't have repeated values)

        #we now insert the incidents that are actually new into the current_incidents (not old ones that have been updated)
        insert_incidents_ids = set(new_incident_ids) - common_incidents_ids 
        insert_incidents = get_rows_from_ids(session, models.Temporary_Incident, insert_incidents_ids)
        insert_incidents = convert_incidents_orm_objects(insert_incidents, models.Current_Incident)    
        write_list_to_db(session, insert_incidents)
        print(f"Added {len(insert_incidents)} new incidents to {models.Current_Incident.__tablename__}")
        

        #we can now check whether any fields have been updated from 'current_incidents' using common_incident_ids
        updated = current_incidents_changed_statuses(session, common_incidents_ids)
        print(f"{len(updated)} incidents have changed statues to inform users")


        #TODO now we can move expired ones to archived  
        
        #if new incident has been updated, the record needs to also be updated


        #we are done with temp table
        flush_db_table(session, models.Temporary_Incident)
        #print results and commit
        if monitor_incident_tables:
                    get_table_info(session, models.Temporary_Incident)
                    get_table_info(session, models.Current_Incident)
                    get_table_info(session, models.Archived_Incident)
        session.commit()

#this can be pushed to users 
def check_for_expired_incidents(session):
    possible_statuses = ['completed', 'safe', 'active', 'controlled', 'contained']
    possible_warning_levels = ['advice', 'none', 'watch_and_act']
    completed = []

    check = get_all_rows(session, models.Current_Incident)
    for incident in check:
        if incident.status == 'completed':
            completed.append(incident)
    
    return completed

#check for status/warning level changes
def current_incidents_changed_statuses(session, checklist_ids):
    updated = []

    #get the rows from the 2 tables to be checked for updates
    old_incidents = get_rows_from_ids(session, models.Current_Incident, checklist_ids) #these are objects
    new_incidents = get_rows_from_ids(session, models.Temporary_Incident, checklist_ids)

    #create 2 dictionaries for easy look up and comparison
    old_incident_by_id = {}
    for incident in old_incidents:
        old_incident_by_id[incident.id] = incident
    new_incident_by_id = {}
    for incident in new_incidents:
        new_incident_by_id[incident.id] = incident

    #compare fields
    for id, old_incident in old_incident_by_id.items():
        new_incident = new_incident_by_id[id]

        #the fields we want to check can be added here
        if old_incident.status != new_incident.status or old_incident.warning_level != new_incident.warning_level:
           updated.append(old_incident)

    #we can return more data if we want. Like what fields have changed
    return updated

#create row in household table
def create_household():
    #TODO
    #generate an id. receive data from client
    pass
 
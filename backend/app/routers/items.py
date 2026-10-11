from app import models
from app.database import get_session
from sqlalchemy.orm import Session
from sqlalchemy import delete
from sqlalchemy import select
from datetime import datetime, timezone

verbose_debug = True
monitor_incident_tables = True
testing_mode = False 
possible_warning_levels = ['advice', 'none', 'watch_and_act']
possible_statuses = ['completed', 'safe', 'active', 'controlled', 'contained']

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
#input a dictionary like {field: value}
def get_db_rows_by_all_fields(session, model, fields):
    query = select(model)

    for field, value in fields.items():
        query = query.where(getattr(model, field) == value) #every time it runs the list gets narrowed down
    rows = session.execute(query).scalars().all()

    if verbose_debug:
        print(
            f"Selected {len(rows)} rows from "
            f"{model.__tablename__} table where {fields}"
        )
    return rows

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
    new_incidents = convert_incidents_orm_objects(incidents, models.Temporary_Incident) 
    new_incident_ids = [incident.id for incident in new_incidents] 
    
    with get_session() as session:
        
        #we need to store the new incidents in a temporary table for logic later (the temporary_incidents should be empty)
        write_list_to_db(session, new_incidents)           #writes to temporary_incidents
        print(f"Added {len(new_incidents)} new incidents to {models.Temporary_Incident.__tablename__}")

        print_incidents_info(session)
        
        existing_incident_ids = get_ids_from_table(session, models.Current_Incident)
        
        #incidents ids that are in common can't be inserted into 'current_incidents'because they already exist
        #they need to be checked to see if the incidents have updated  
        common_incidents_ids = set(new_incident_ids) & set(existing_incident_ids) 

        #we now insert the incidents that are actually new into the current_incidents (not old ones that have been updated)
        insert_incidents_ids = set(new_incident_ids) - common_incidents_ids 
        insert_incidents = get_rows_from_ids(session, models.Temporary_Incident, insert_incidents_ids)
        insert_incidents = convert_incidents_orm_objects(insert_incidents, models.Current_Incident)    
        write_list_to_db(session, insert_incidents)
        print(f"Added {len(insert_incidents)} new incidents to {models.Current_Incident.__tablename__}")
        
        #we can now check whether any fields have been updated from 'current_incidents' using common_incident_ids
        #updates is a nested dictionary like this -> { id: { field: new status } }  
        notification_fields  = ["status", "warning_level", "latitude", "longitude", "description", "address"]
        user_updates = current_incidents_changed_values(session, common_incidents_ids, notification_fields )
        print(f"{len(user_updates)} incidents have changed statues to inform users")
        if verbose_debug:
            print(f"Updated incidents: {user_updates}")
        update_incident_table(session, models.Current_Incident, user_updates) 

        #many incidents will also have an updated 'last_updated' value which also needs to be written
        timestamp_updates = current_incidents_changed_values(session, common_incidents_ids, ["last_updated"])
        update_incident_table(session, models.Current_Incident, timestamp_updates)
        print(f"{len(timestamp_updates)} incidents have had timestamp updates")

        #now we get any incidents that have expired or had their statuses changed to 'completed'
        expired_incidents = get_expired_incidents(session, models.Current_Incident)
        completed_incidents = get_db_rows_by_all_fields(session, models.Current_Incident, {"status": "completed"})
        print(f"{len(expired_incidents)} incidents have expired")
        print(f"{len(completed_incidents)} incidents have expired")

        #remove expired and completed incidents from current_incidents and add them to archived_incidents
        expired_incident_ids = [incident.id for incident in expired_incidents] 
        completed_incident_ids = [incident.id for incident in completed_incidents]
        remove_incidents_ids = set(expired_incident_ids) | set(completed_incident_ids)
        remove_incidents = get_rows_from_ids(session, models.Current_Incident, remove_incidents_ids)
        delete_db_rows(session, remove_incidents)
        print(f"Removed {len(remove_incidents)} from current_incidents")

        #append the deleted rows to archived_incidents
        archived_incidents = convert_incidents_orm_objects(remove_incidents, models.Archived_Incident)
        
        #TODO the archived table needs to be checked to make sure the same incident isn't inserted twice 
        
        write_list_to_db(session, archived_incidents)

        #we are done with temp table
        flush_db_table(session, models.Temporary_Incident)
        
        #print table info and commit
        print_incidents_info(session)
        session.commit()

#this can be pushed to users 
def get_expired_incidents(session, model):
    check = get_all_rows(session, model)
    expired = []
    time_now = datetime.now(timezone.utc)

    for incident in check:
        if incident.expires == None:
            break 
        expiry_time =  incident.expires 
        if expiry_time < time_now:
            expired.append(incident)

    return expired

#check for status/warning level changes
def current_incidents_changed_values(session, checklist_ids, check_fields):
    updated = {}

    #get the rows from the 2 tables to be checked for updates
    old_incidents = get_rows_from_ids(session, models.Current_Incident, checklist_ids) 
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
        changed_fields = {}

        for field in check_fields:
            old_value = getattr(old_incident, field)
            new_value = getattr(new_incident, field)
            if old_value != new_value:
                changed_fields[field] = new_value

        if changed_fields:
            updated[id] = changed_fields

    return updated

def update_incident_table(session, model, updates):
    #extract the rows to update by their ids (the keys from updates)
    updated_rows = get_rows_from_ids(session, model, list(updates))

    #remember updates are like this -> { id: { field: new status } }
    for row in updated_rows:
        updated_fields = updates[row.id]
        
        for field, new_value in updated_fields.items():
            setattr(row, field, new_value)

def print_incidents_info(session):
    get_table_info(session, models.Temporary_Incident)
    get_table_info(session, models.Current_Incident)
    get_table_info(session, models.Archived_Incident)


#create row in household table
def create_household():
    #TODO
    #generate an id. receive data from client
    pass
 
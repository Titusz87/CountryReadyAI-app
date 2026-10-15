from app import models
from app.database import get_session
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import app.services.db_helpers as db
from app.services.quadtree import Quadtree
import numpy as np
from sklearn.neighbors import BallTree

#------------------script vars-----------------------
quadtree = None
UNSAFE_BUSHFIRE_DISTANCE = 10

#---------------------config---------------------------------

verbose_debug = False
custom_quadtree = False
notification_fields  = ["status", "warning_level", "latitude", "longitude", "description", "address"] #people get updated when these fields change

#-------------------------------info-----------------------------------------

possible_warning_levels = ['advice', 'none', 'watch_and_act']
possible_statuses = ['completed', 'safe', 'active', 'controlled', 'contained']

#--------------------------fn's called from other scripts-----------------------------------------------

#this fn is called from the polling script
#this is complicated. Please don't touch it!
def update_database_incidents(incidents):
    with get_session() as session:
        
        print("Updating db records...")
            
        #need to turn our incidents class into proper table objects before writing them to db
        #we need to compare the ids of things because they are unique (objects may not be)
        #we need to store the new incidents in a temporary table for logic later (temporary_incidents should be empty)
        new_incidents = db.convert_incidents_orm_objects(incidents, models.Temporary_Incident) 
        new_incident_ids = [incident.id for incident in new_incidents] 
        db.write_list_to_db(session, new_incidents)          
        print(f"Added {len(new_incidents)} new incidents to {models.Temporary_Incident.__tablename__}")

        print_incidents_info(session)

        # #we now insert the incidents that are actually new into the current_incidents (not old ones that have been updated)
        existing_incident_ids = db.get_ids_from_table(session, models.Current_Incident)
        insert_incidents_ids = get_new_ids_safe(existing_incident_ids, new_incident_ids)
        insert_incidents = db.get_rows_from_ids(session, models.Temporary_Incident, insert_incidents_ids)
        insert_incidents = db.convert_incidents_orm_objects(insert_incidents, models.Current_Incident)    
        db.write_list_to_db(session, insert_incidents)
        print(f"Added {len(insert_incidents)} new incidents to current_incidents")
        db.print_table_info(session, models.Current_Incident)
        
        #we can now check whether any fields have been updated from 'current_incidents' using common_incident_ids
        #updates is a nested dictionary like this -> { id: { field: new status } }  
        global notification_fields  
        common_incidents_ids = set(new_incident_ids) & set(existing_incident_ids)
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
        #note: expired and completed incidents will keep getting pulled from dataquoll API. need to make sure that users aren't informed more than once
        expired_incidents = get_expired_incidents(session, models.Current_Incident)
        completed_incidents = db.get_db_rows_by_all_fields(session, models.Current_Incident, {"status": "completed"})
        print(f"{len(expired_incidents)} incidents have expired")
        print(f"{len(completed_incidents)} incidents have 'completed' status")

        #figure out which incidents in current_incidents have expired or completed  
        expired_incident_ids = [incident.id for incident in expired_incidents] 
        completed_incident_ids = [incident.id for incident in completed_incidents]
        remove_incidents_ids = set(expired_incident_ids) | set(completed_incident_ids)
        
        #figure out which incidents need to be archived (where ids don't already exist in archived_incidents)
        existing_archived_ids = db.get_ids_from_table(session, models.Archived_Incident)
        new_archived_ids = get_new_ids_safe(existing_archived_ids, remove_incidents_ids)
        new_archived_incidents = db.get_rows_from_ids(session, models.Current_Incident, new_archived_ids)
        new_archived_incidents = db.convert_incidents_orm_objects(new_archived_incidents, models.Archived_Incident) 
        db.write_list_to_db(session, new_archived_incidents)
        print(f"Archived {len(new_archived_incidents)} incidents")

        #can delete the rows in current_incidents that were archived now
        remove_incidents = db.get_rows_from_ids(session, models.Current_Incident, remove_incidents_ids)
        db.delete_db_rows(session, remove_incidents)
        print(f"Removed {len(remove_incidents)} incidents from current_incidents")

        #we are done with temp table. Print table info and commit
        db.flush_db_table(session, models.Temporary_Incident)
        print_incidents_info(session)
        
        #now the current incidents have been rewritten, create quadtree for nearby incident lookup and rewrite table
        nearby_incident_data = use_quadtree(session)
        people_to_incident_rows = db.get_all_rows(session, models.People_Incident)
        for row in people_to_incident_rows: 
            row.incident_ids = nearby_incident_data.get(row.id)
        nearby_incident_count = sum(1 for person_id, incident_ids in nearby_incident_data.items() if incident_ids)
        print(f"{nearby_incident_count} people have nearby incidents occurring")


        #TODO now actually update everyone 
            

        session.commit()


#------------------------------helpers------------------------------------------------------------

#This can be pushed to users
def get_expired_incidents(session, model):
    check = db.get_all_rows(session, model)
    expired = []
    time_now = datetime.now(timezone.utc)

    for incident in check:
        if incident.expires is None:
            continue
        expiry_time = incident.expires
        if expiry_time.tzinfo is None:
            expiry_time = expiry_time.replace(tzinfo=timezone.utc)
        if expiry_time < time_now:
            expired.append(incident)
    return expired

#check for status/warning level changes
def current_incidents_changed_values(session, checklist_ids, check_fields):
    updated = {}

    #get the rows from the 2 tables to be checked for updates
    old_incidents = db.get_rows_from_ids(session, models.Current_Incident, checklist_ids) 
    new_incidents = db.get_rows_from_ids(session, models.Temporary_Incident, checklist_ids)

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
    updated_rows = db.get_rows_from_ids(session, model, list(updates))

    #remember updates are like this -> { id: { field: new status } }
    for row in updated_rows:
        updated_fields = updates[row.id]
        
        for field, new_value in updated_fields.items():
            setattr(row, field, new_value)

def print_incidents_info(session):
    db.print_table_info(session, models.Temporary_Incident)
    db.print_table_info(session, models.Current_Incident)
    db.print_table_info(session, models.Archived_Incident)

def get_new_ids_safe(old_ids, new_ids):
    in_common_ids = set(old_ids) & set(new_ids)
    truly_new_ids = set(new_ids) - in_common_ids
    return truly_new_ids

def use_quadtree(session):
    current_incident_rows = db.get_all_rows(session, models.Current_Incident)
    people = db.get_all_rows(session, models.People)
    results = {}
    print("Spatially partitioning incidents for user location updates...")
    
    if custom_quadtree:
        #extract only relevant data    
        incident_points = [Quadtree.IncidentPoint(row.latitude, row.longitude, row.id) for row in current_incident_rows]
        global quadtree
        quadtree = Quadtree(incident_points)

        #people need to 'subscribe' to nearby incidents 
        #get nearby incidents for all people via the quadtree
        print("Finding incidents nearby to people in db...")
        people_locations = [Quadtree.IncidentPoint(person.latitude,person.longitude,person.id) for person in people]
        results = {person.id: [] for person in people_locations}
        for person in people_locations:
            found_incidents = quadtree.find_nearby_incidents(person,UNSAFE_BUSHFIRE_DISTANCE)
            results[person.id] = [incident.id for incident in found_incidents]
    else:
        #this is the solution from a balltree library 
        incident_coords = np.radians([[row.latitude, row.longitude] for row in current_incident_rows])
        people_coords = np.radians([[person.latitude, person.longitude] for person in people])
        tree = BallTree(incident_coords, metric="haversine")
        radius_radians = UNSAFE_BUSHFIRE_DISTANCE / 6371.0
        results_indices = tree.query_radius(people_coords, r=radius_radians)
        for person, incident_indices in zip(people, results_indices):
            results[person.id] = [current_incident_rows[i].id for i in incident_indices]

    if verbose_debug:
        print(results)
    return results

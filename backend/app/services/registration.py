from app.routers import registration
from app.models import People
from app.database import get_session
import app.services.db_helpers as db 

def create_person(latitude, longitude):
    with get_session() as session:

        #create new person (generic id for receiving emergency updates)
        #remember id is auto generated as according to logic in 'models'
        person = People(
            latitude = latitude, 
            longitude = longitude, 
            household_id = None,                        
            community_leader_id = None
        )
        db.write_list_to_db(session, [person])
        session.commit()
        return person.id



#create row in household table
def create_household():
    #TODO
    #generate an id. receive data from client
    pass 
import httpx
import os
from dotenv import load_dotenv
import json

class Incident:
    def __init__(self, id, properties):
        self.id = id
        self.event_type = properties["eventType"]
        self.status = properties["status"]
        self.warning_level = properties["warningLevel"]
        self.state = properties["location"]["state"]
        self.latitude = properties["location"]["latitude"]
        self.longitude = properties["location"]["longitude"]
        self.reported_time = properties["timestamps"]["reported"]
        self.last_updated = properties["timestamps"]["updated"]
        
        #these fields may not have any data and probably shouldn't be used 
        self.expires = properties["details"].get("expires")
        self.description = properties["details"].get("description")
        self.address = properties["location"].get("address")

    #vars is a dict of all object fields 
    def check_values_set(self):
        print(self.id)
        for attribute, value in vars(self).items():
            if value is None:
                print(f"{attribute} is not set")
        print("\n")

  

#-------local vars------------------------------------------------
polled_incidents = []
states = ["nsw", "vic", "qld", "wa", "sa", "tas", "act", "nt"]
event_types = set()
statuses = set()
warning_levels = set()

#----------------------------------------------------------

#---------------------------------------------------------
#get API key from env file 
load_dotenv(".env")
API_KEY = os.getenv("Authorization")
#check the key is set properly 
if not API_KEY:
    raise RuntimeError("dataquoll api key is not set")
#-----------------------------------------------------------
async def poll_all_states():
    for s in states:
        await poll_dataquoll_by_state(s)
        print(f"Polled state: {s}")

    update_attribute_sets()
    return "hey"

#get state data from dataquoll api
async def poll_dataquoll_by_state(state):
    #construct the command "curl "https://dataquoll.io/api/v1/incidents" -H "Authorization: Bearer YOUR_API_KEY"
    url = "https://dataquoll.io/api/v1/incidents"
    #the -H flag for html headers
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    #can set other params like this. Best to poll each individual state rather than everywhere at once because the 'limit' may not work 
    params = {
        "state": state,
        "format": "json",
        #500 is max
        "limit": 500       #need to do a check while creating incident objects to ensure that the limit doesn't equal the number of incidents (suggesting that there are more incidents that haven't been scraped)
    }
    
    #await the response from dataquoll as json 
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()    #this is a python dictionary  
        create_json_objects(data) #sort out our json objects

        return data

def create_json_objects(data):
    features = data["features"]
    for feature in features:
        #grab these 2 json chunks and create incident object
        id = feature["id"]
        properties = feature["properties"]
        incident = Incident(id, properties)

        #incident.check_values_set()
        polled_incidents.append(incident)
        
def update_attribute_sets():
    for i in polled_incidents:
        event_types.add(i.event_type)
        statuses.add(i.status)
        warning_levels.add(i.warning_level)

    print(f"Event Types: {event_types}")
    print(f"Statuses: {statuses}")
    print(f"Warning Levels: {warning_levels}")


        


    
    
    
   



from fastapi import APIRouter
from pydantic import BaseModel
from app.services.registration import create_person

router = APIRouter()

#--------------------------------------------------------------------------------
class StartupRequest(BaseModel):
    latitude: float
    longitude: float

#this is the route that runs ONCE when a device connects for the first time (to give the device a unique id)
@router.post("/first-app-launch")
def first_app_launch(data: StartupRequest):
    person_id = create_person(
        latitude=data.latitude,
        longitude=data.longitude
    )

    return {
        "status": "ok",
        "message": "Device registered successfully",
        "person_id": person_id
    }

#TODO this needs to be safe (if a network failure happens the device can't create 2 people entries)

#-----------------------------------------------------------------------------------------

#TODO the /startup POST that sends location when the app launches again
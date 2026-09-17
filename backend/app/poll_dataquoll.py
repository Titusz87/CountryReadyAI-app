import httpx
import os
from dotenv import load_dotenv

#get API key from env file 
load_dotenv(".env")
API_KEY = os.getenv("Authorization")
#check the key is set properly 
if not API_KEY:
    raise RuntimeError("dataquoll api key is not set")

#get data from dataquoll api
async def poll_dataquoll():
    #construct the command "curl "https://dataquoll.io/api/v1/incidents?state=nsw&format=csv" -H "Authorization: Bearer YOUR_API_KEY"
    url = "https://dataquoll.io/api/v1/incidents"
    #the -H flag for html headers
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    #other params in the link
    params = {
        "state": "nsw",
        "format": "json",
        "limit": 200
    }
    
    #await the response from dataquoll as json 
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data

        
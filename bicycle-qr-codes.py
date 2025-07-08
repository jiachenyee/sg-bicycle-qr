import asyncio
import os
import aiohttp
import json
import datetime

from dotenv import load_dotenv, dotenv_values 

load_dotenv()

# fetch datamall api key from env
API_ENDPOINT = os.getenv("API_ENDPOINT")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")

HEADER_PREFIX = os.getenv("HEADER_PREFIX")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

async def request(lat: float, long: float):
    pass
    # http_session = aiohttp.ClientSession()
    
    # params = {
    #     'Lat': lat,
    #     'Long': long,
    #     'Dist': dist # distance in km
    # }

    # headers = {
    #     'Accept': 'application/json',
    #     'Accountkey': DATAMALL_API_KEY,
    #     'Content-Type': 'application/json'
    # }

    # async with http_session.get("https://datamall2.mytransport.sg/ltaodataservice/BicycleParkingv2", params=params, headers=headers) as response:
    #     response.raise_for_status()
    #     result = await response.json()
        
    #     return result
    
    # await http_session.close()

async def map_entire_country():
    pass

async def main():
    # await map_entire_country()
    
    with open("data/last_updated.txt", "w") as f:
        f.write(datetime.datetime.now().isoformat())
        f.close()
    
asyncio.run(main())

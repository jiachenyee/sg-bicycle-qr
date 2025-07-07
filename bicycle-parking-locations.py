import asyncio
import os
import aiohttp
import json

from dotenv import load_dotenv, dotenv_values 

load_dotenv() 

# fetch datamall api key from env
DATAMALL_API_KEY = os.getenv("DATAMALL_API_KEY")

async def request(lat: float, long: float, dist: int = 5):
    http_session = aiohttp.ClientSession()
    
    params = {
        'Lat': lat,
        'Long': long,
        'Dist': dist # distance in km
    }

    headers = {
        'Accept': 'application/json',
        'Accountkey': DATAMALL_API_KEY,
        'Content-Type': 'application/json'
    }

    async with http_session.get("https://datamall2.mytransport.sg/ltaodataservice/BicycleParkingv2", params=params, headers=headers) as response:
        response.raise_for_status()
        result = await response.json()
        
        return result
    
    await http_session.close()

async def map_entire_country():
    survey_points = [
        [1.43474, 103.677115],
        [1.43474, 103.74844],
        [1.43474, 103.81976499999999],
        [1.43474, 103.89108999999999],
        [1.43474, 103.962415],
        [1.3634150000000007, 103.6414525],
        [1.3634150000000007, 103.7127775],
        [1.3634150000000007, 103.7841025],
        [1.3634150000000007, 103.85542749999999],
        [1.3634150000000007, 103.92675249999999],
        [1.3634150000000007, 103.9980775],
        [1.2920900000000013, 104.03374],
        [1.2920900000000013, 103.962415],
        [1.2920900000000013, 103.89108999999999],
        [1.2920900000000013, 103.81976499999999],
        [1.2920900000000013, 103.74844],
        [1.2920900000000013, 103.677115],
        [1.2920900000000013, 103.60579],
        [1.220765000000002, 103.6414525],
        [1.220765000000002, 103.7127775],
        [1.220765000000002, 103.7841025],
        [1.220765000000002, 103.85542749999999]
    ]

    all_my_glorious_bicycle_parking_locations = await asyncio.gather(
        *[request(lat, long) for lat, long in survey_points]
    )

    all_parking_locations = []

    for parking_set in all_my_glorious_bicycle_parking_locations:
        json_data = json.loads(json.dumps(parking_set))
        # print(json_data)

        if json_data['value'] != None:
            all_parking_locations += json_data['value']


    all_parking_locations = list(map(dict, set(tuple(sorted(d.items())) for d in all_parking_locations)))
    # save to bicycle_parking_locations.json
    with open('bicycle_parking_locations.json', 'w') as f:
        json.dump(all_parking_locations, f, indent=2)
    print("All bicycle parking locations saved to bicycle_parking_locations.json")

async def main():
    await map_entire_country()
    
asyncio.run(main())

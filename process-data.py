import json

with open('potato.json', 'r') as file:
    data = json.load(file)["data"]

with open('data/bicycle_parking_locations.json', 'r') as file:
    bicycle_parking_locations = json.load(file)

processed_data = []

for location in bicycle_parking_locations:
    processed_item = {
        "name": location["Description"],
        "latitude": location["Latitude"],
        "longitude": location["Longitude"],
        "rackCount": location["RackCount"],
        "rackType": location["RackType"],
        "shelterIndicator": location["ShelterIndicator"]
    }
    
    for datum in data:
        if (abs(processed_item['latitude'] - datum['lat']) < 0.0001 and
            abs(processed_item['longitude'] - datum['lng']) < 0.0001):
            processed_item['qr'] = datum['qrCode']
            data.remove(datum)
            break
    
    processed_data.append(processed_item)

with open('processed_bicycle_parking_locations.json', 'w') as file:
    json.dump({"data": processed_data}, file, indent=2)
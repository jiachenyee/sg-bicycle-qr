import pandas as pd
import json

with open("data/bicycle_parking_locations.json", "r") as file:
    data_json = json.load(file)["data"]
df = pd.json_normalize(data_json)
df.to_csv("data/bicycle_parking_locations.csv")

import pandas as pd


df = pd.read_csv("data/bicycle_parking_locations.csv", index_col=0)


# remove missing data
df = df.dropna(subset=["rackType"])


# clean up rackType
df["rackType"] = df["rackType"].str.upper()
df["rackType"] = df["rackType"].replace("YELLOW BOX", "YELLOWBOX")
df["rackType"] = df["rackType"].str.replace("YELLOW_BOX", "YELLOWBOX")
df["rackType"] = df["rackType"].replace("RACKS_PA", "PA_RACKS")
df["rackType"] = df["rackType"].replace("HBD_RACKS", "HDB_RACKS")


# split rackType into 2 columns
df["rackType"] = df["rackType"].replace("YELLOWBOX", "_YELLOWBOX")
df[["organisation", "rackType"]] = df["rackType"].str.split("_", n=1, expand=True)


# reorder and rename columns
df = df.rename(columns={"rackCount": "capacity", "shelterIndicator": "isSheltered"})
df = df[
    [
        "name",
        "latitude",
        "longitude",
        "capacity",
        "rackType",
        "organisation",
        "isSheltered",
        "qr",
    ]
]


# output
df.to_csv("data/cleaned_bicycle_parking_locations.csv")

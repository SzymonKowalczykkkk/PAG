from pymongo import MongoClient
import pymongo
import json
import os

url = "mongo_db_url"
client = MongoClient(url)

def add_data(name_file, folder_name):
    geojson_data = os.path.join(folder_name, name_file)
    geojson_data = name_file

    try:
        with open(geojson_data, 'r', encoding='utf-8-sig') as f:
            geojson_data = json.load(f)
        adm = client.administracja
        woj = adm.wojewodztwa
        for feature in geojson_data["features"]:
            document = {
                "properties": feature["properties"],
                # "name": feature["properties"].get("name", "Unnamed"),  # Use "Unnamed" if no name is present
                "geometry": feature["geometry"]
            }
            woj.insert_one(document)

    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)

def main():
    folder_name = r"powiaty"
    for file in os.listdir(folder_name):
        if file.endswith(".geojson"):
            add_data(file, folder_name)
    adm = client.administracja
    woj = adm.wojewodztwa

if __name__ == "__main__":
    main()
# Autorzy: Szymon Kowalczyk, Weronika Kałowska, Krzysztof Rutkowski
from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import os
import pymongo
from pymongo import MongoClient
import redis
from bson import ObjectId
import json
import hashlib
import pandas as pd

# r = redis.Redis(
# host='redis-15280.c55.eu-central-1-1.ec2.redns.redis-cloud.com',
# port=15280,
# decode_responses=True,
# username="default",
# password="7m8lWRkGUY7C10hSvWRpx3Tnj6cqay65",
# )
# lat =52.28138888888889
# lng =20.96333333333333
# date = "2024-11-01"
# def generuj_klucz(szerokosc, dlugosc):
#     surowy_klucz = f"{szerokosc}:{dlugosc}"
#     hash_klucz = hashlib.md5(surowy_klucz.encode()).hexdigest()
#     return hash_klucz
# year, month, day = date.split("-")
# kod_str = r.get(generuj_klucz(lat, lng))
# kod_list = kod_str.split(', ')
# id = kod_list[0]
# print(kod_list[0])
# name = kod_list[1]

# Ustworzenie api
app = FastAPI()
url = "mongodb+srv://weronika:PAG2@cluster0.gymzp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(url)

# Ustawienie rzeczy potrzebnych do działania api ze stroną
app.mount("/static", StaticFiles(directory="static"), name="static")

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

@app.get("/pol")
def fetchPol():
    try:
        database = client.get_database("administracja")
        country_collection = database.kraj
        country_cursor = country_collection.find()
        country_list = list(country_cursor)
        print("Done!")
        return JSONResponse(content=json.loads(JSONEncoder().encode(country_list)))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/woj")
def fetchWoj():
    try:
        database = client.get_database("administracja")
        woj_collection = database.wojewodztwa
        woj_cursor = woj_collection.find()
        woj_list = list(woj_cursor)
        print("Done!")
        return JSONResponse(content=json.loads(JSONEncoder().encode(woj_list)))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/pow")
def fetchPow(teryt: str):
    try:
        database = client.get_database("administracja")
        pow_collection = database.powiaty

        pow_cursor = pow_collection.find({"features.properties.national_c": {"$regex": f"^{teryt}", "$options": "i"}})
        pow_list = list(pow_cursor)
        print(len(pow_list))
        return JSONResponse(content=json.loads(JSONEncoder().encode(pow_list)))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/points")
def fetchPoint(teryt: str,date: str, dane:str,pora: str):
    try:
        r = redis.Redis(
            host='redis-15280.c55.eu-central-1-1.ec2.redns.redis-cloud.com',
            port=15280,
            decode_responses=True,
            username="default",
            password="7m8lWRkGUY7C10hSvWRpx3Tnj6cqay65",
        )
        points_str = r.get(teryt)
        points_list = [tuple(map(float, point.split(','))) for point in points_str.split(';')]
        return points_list
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/weatherData")
def fetchData(lng, lat, date: str, dane:str,pora: str):
    r = redis.Redis(
        host='redis-15280.c55.eu-central-1-1.ec2.redns.redis-cloud.com',
        port=15280,
        decode_responses=True,
        username="default",
        password="7m8lWRkGUY7C10hSvWRpx3Tnj6cqay65",
    )
    def generuj_klucz(szerokosc, dlugosc):
        surowy_klucz = f"{szerokosc}:{dlugosc}"
        hash_klucz = hashlib.md5(surowy_klucz.encode()).hexdigest()
        return hash_klucz
    year, month, day = date.split("-")
    kod_str = r.get(generuj_klucz(lat, lng))
    kod_list = kod_str.split(', ')
    id = kod_list[0]
    name = kod_list[1]

    if dane == "temperatura":
        temperatura_dane = ["B00300S", "B00305A"]
        df_air = pd.read_csv(f"{temperatura_dane[0]}_{year}_{month}.csv", sep=';', header=None)
        df_gro = pd.read_csv(f"{temperatura_dane[1]}_{year}_{month}.csv", sep=';', header=None)
        filtered_rows_air = df_air[(df_air[0] == id) & (df_air[2].astype(str).str.startswith(f"{year}_{month}_{day}"))]
        filtered_rows_gro = df_gro[(df_gro[0] == id) & (df_gro[2].astype(str).str.startswith(f"{year}_{month}_{day}"))]
        temp_air = filtered_rows_air[3].tolist()
        temp_gro = filtered_rows_gro[3].tolist()
        return temp_air.mean, temp_air.median, temp_gro.mean, temp_gro.median
    elif dane == "opady":
        opady_dane = ["B00608S", "B00604S", "B00802A", "B00910A"]

        df_opady10min = pd.read_csv(f"{opady_dane[0]}_{year}_{month}.csv", sep=';', header=None)
        df_opadDobowy = pd.read_csv(f"{opady_dane[1]}_{year}_{month}.csv", sep=';', header=None)
        df_wilgotnosc = pd.read_csv(f"{opady_dane[2]}_{year}_{month}.csv", sep=';', header=None)
        df_snieg = pd.read_csv(f"{opady_dane[3]}_{year}_{month}", sep=';', header=None)

        opady10min = df_opady10min[(df_opady10min[0] == id) & (df_opady10min[2].astype(str).str.startswith(f"{year}_{month}_{day}"))]
        opadDobowy = df_opadDobowy[(df_opadDobowy[0] == id) & (df_opadDobowy[2].astype(str).str.startswith(f"{year}_{month}_{day}"))]
        wilgotnosc = df_wilgotnosc[(df_wilgotnosc[0] == id) & (df_wilgotnosc[2].astype(str).str.startswith(f"{year}_{month}_{day}"))]
        snieg = df_snieg[(df_snieg[0] == id) & (df_snieg[2].astype(str).str.startswith(f"{year}_{month}_{day}"))]

        return opady10min.mean(), opady10min.median(), opadDobowy, wilgotnosc.mean, wilgotnosc.median, snieg.mean, snieg.median

    elif dane == "wiatr":
        wiatr_dane = ["B00702A", "B00703A", "B00714A"]

        df_sredpred = pd.read_csv(f"{wiatr_dane[0]}_{year}_{month}.csv", sep=';', header=None)
        df_maxpred = pd.read_csv(f"{wiatr_dane[1]}_{year}_{month}.csv", sep=';', header=None)
        df_maxporyw = pd.read_csv(f"{wiatr_dane[2]}_{year}_{month}.csv", sep=';', header=None)

        sredpred = df_sredpred[(df_sredpred[0] == id) & (df_sredpred[2].astype(str).str.startswith(f"{year}_{month}_{day}"))]
        max_maxpred = df_maxpred[df_maxpred[0] == id][3].max()
        max_maxporyw = df_maxporyw[df_maxporyw[0] == id][3].max()

        return sredpred.mean, sredpred.median, max_maxpred, max_maxporyw

@app.get("/")
def read_root():
    return FileResponse(os.path.join("static", "index.html"))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
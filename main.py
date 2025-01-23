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

# Ustworzenie api
app = FastAPI()
r = redis.Redis(
    host='redis-15280.c55.eu-central-1-1.ec2.redns.redis-cloud.com',
    port=15280,
    decode_responses=True,
    username="default",
    password="7m8lWRkGUY7C10hSvWRpx3Tnj6cqay65",
)
points_str = r.get("0226")
points_list = [tuple(map(float, point.split(','))) for point in points_str.split(';')]
print(points_list)
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
        print(points_list)
        return JSONResponse(content=json.dumps(points_list))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/")
def read_root():
    return FileResponse(os.path.join("static", "index.html"))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
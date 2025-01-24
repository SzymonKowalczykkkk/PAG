# Autorzy: Szymon Kowalczyk, Weronika Kałowska, Krzysztof Rutkowski

# Import potrzebnych bibliotek
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

# Ustworzenie api
app = FastAPI()

# Deklaracja klienta i połączenie się z chmurą MongoDB
url = "mongodb+srv://weronika:PAG2@cluster0.gymzp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(url)

# Dekalracja funckji do poprawnego kodowania plików json
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Dekalracja requset złużący stronie wstępnego pobrania poligonu podkładowego z bazy MongoDB
@app.get("/pol")
def fetchPol():
    try:
        # Połączenie z konkretną bazą w chmurze
        database = client.get_database("administracja")

        # Określenie wyszukiwanej kolekcji
        country_collection = database.kraj

        # Pobranie wszystkich obieków(obiektu) z danej kolecji i wysłanie ich na strone w formie geojson
        country_cursor = country_collection.find()
        country_list = list(country_cursor)
        return JSONResponse(content=json.loads(JSONEncoder().encode(country_list)))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Dekalracja requset złużący stronie do pobrania poligonu województw z bazy MongoDB
@app.get("/woj")
def fetchWoj():
    try:
        # Połączenie z konkretną bazą w chmurze
        database = client.get_database("administracja")

        # Określenie wyszukiwanej kolekcji
        woj_collection = database.wojewodztwa

        # Pobranie wszystkich obieków z danej kolecji i wysłanie ich na strone w formie geojson
        woj_cursor = woj_collection.find()
        woj_list = list(woj_cursor)
        return JSONResponse(content=json.loads(JSONEncoder().encode(woj_list)))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Dekalracja requset złużący stronie do pobrania poligonu powiatów z bazy MongoDB. Request przyjmuje atrybut teryt.
@app.get("/pow")
def fetchPow(teryt: str):
    try:
        # Połączenie z konkretną bazą w chmurze
        database = client.get_database("administracja")

        # Określenie wyszukiwanej kolekcji
        pow_collection = database.powiaty

        # Pobranie obieków z danej kolecji, których atrybut national_c zaczyna się od przesłanego ze strony terytu
        # i wysłanie ich na strone w formie geojson
        pow_cursor = pow_collection.find({"features.properties.national_c": {"$regex": f"^{teryt}", "$options": "i"}})
        pow_list = list(pow_cursor)
        return JSONResponse(content=json.loads(JSONEncoder().encode(pow_list)))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Dekalracja requset złużący stronie do pobrania współrzędnych punktów z bazy Redis. Request przyjmuje atrybut teryt.
# Inne atrybuty przesłane przez request są nie używane, ale z obserwacji wynika że innaczej system przestaje działać.
@app.get("/points")
def fetchPoint(teryt: str,date: str, dane:str,pora: str):
    try:
        # Deklaracja połączenia z bazą danych Redis
        r = redis.Redis(
            host='redis-15280.c55.eu-central-1-1.ec2.redns.redis-cloud.com',
            port=15280,
            decode_responses=True,
            username="default",
            password="7m8lWRkGUY7C10hSvWRpx3Tnj6cqay65",
        )

        # Pobranie punktów znajdujących się w powiacie o przesłanym kodzie teryt
        points_str = r.get(teryt)
        points_list = [tuple(map(float, point.split(','))) for point in points_str.split(';')]
        # Punkty są przesyłane jako json(czasami nie).
        return points_list
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Dekalracja requset złużący stronie do pobrania określonych danych pogodowych z plików w folderze lokalnym
@app.get("/weatherData")
def fetchData(lng, lat, date: str, dane:str,pora: str):
    # Deklaracja połączenia z bazą danych Redis
    r = redis.Redis(
        host='redis-15280.c55.eu-central-1-1.ec2.redns.redis-cloud.com',
        port=15280,
        decode_responses=True,
        username="default",
        password="7m8lWRkGUY7C10hSvWRpx3Tnj6cqay65",
    )

    # Deklaracja funkcj generującej klucze punktów z bazy redis na podstawie ich długości i szerokości
    def generuj_klucz(szerokosc, dlugosc):
        surowy_klucz = f"{szerokosc}:{dlugosc}"
        hash_klucz = hashlib.md5(surowy_klucz.encode()).hexdigest()
        return hash_klucz

    # Deklaracja potrzebnych zmiennych
    year, month, day = date.split("-")
    kod_str = r.get(generuj_klucz(lat, lng))
    kod_list = kod_str.split(', ')
    id = kod_list[0]
    name = kod_list[1]
    if dane == "temperatura":
        # Jeżeli rodzaj wybranych danych do temperatura program czyta odpowiednie pliki csv na dysku lokalnym
        # i wybiera wiersze o określonej dacie i id stacji. Czasami nie działa. Podejrzewamy że jest to spowodowane
        # chwilowym brakiem działania bazy chmurowej Redis.
        print(type(id))
        temperatura_dane = ["B00300S", "B00305A"]
        df_air = pd.read_csv(rf"C:\Users\krisr\OneDrive\Pulpit\PAG2\p2\{temperatura_dane[0]}_{year}_{month}.csv", sep=';', header=None)
        df_air[0] = df_air[0].astype(str).str.strip()
        df_air[2] = df_air[2].astype(str).str.strip()
        filtered_rows_air = df_air[(df_air[0] == id) & (df_air[2].str.startswith(f"{year}-{month}-{day}"))]
        temp_air = filtered_rows_air[3].tolist()
        temp_air = pd.Series(filtered_rows_air[3])
        print(temp_air.mean())

        df_gro = pd.read_csv(rf"C:\Users\krisr\OneDrive\Pulpit\PAG2\p2\{temperatura_dane[1]}_{year}_{month}.csv",sep=';', header=None)
        df_gro[0] = df_gro[0].astype(str).str.strip()
        df_gro[2] = df_gro[2].astype(str).str.strip()
        filtered_rows_gro = df_gro[(df_gro[0] == id) & (df_gro[2].str.startswith(f"{year}-{month}-{day}"))]
        temp_gro = filtered_rows_gro[3].tolist()
        temp_gro = pd.Series(filtered_rows_gro[3])
        print(temp_gro.mean())
        return temp_air.mean(), temp_air.median(), temp_gro.mean(), temp_gro.median(), temp_air.max(), temp_gro.max(), name
    # Nie dopracowany kod. Nie zawsze działa. Wymaga dopraacowania.
    # elif dane == "opady":
    #     opady_dane = ["B00608S", "B00604S", "B00802A", "B00910A"]
    #
    #     df_opady10min = pd.read_csv(f"{opady_dane[0]}_{year}_{month}.csv", sep=';', header=None)
    #     df_opadDobowy = pd.read_csv(f"{opady_dane[1]}_{year}_{month}.csv", sep=';', header=None)
    #     df_wilgotnosc = pd.read_csv(f"{opady_dane[2]}_{year}_{month}.csv", sep=';', header=None)
    #     df_snieg = pd.read_csv(f"{opady_dane[3]}_{year}_{month}", sep=';', header=None)
    #     df_opady10min[0] = df_opady10min[0].astype(str).str.strip()
    #     df_opady10min[2] = df_opady10min[2].astype(str).str.strip()
    #     df_opadDobowy[0] = df_opadDobowy[0].astype(str).str.strip()
    #     df_opadDobowy[2] = df_opadDobowy[2].astype(str).str.strip()
    #     df_wilgotnosc[0] = df_wilgotnosc[0].astype(str).str.strip()
    #     df_wilgotnosc[2] = df_wilgotnosc[2].astype(str).str.strip()
    #     df_snieg[0] = df_snieg[0].astype(str).str.strip()
    #     df_snieg[2] = df_snieg[2].astype(str).str.strip()
    #     filtered_opad10min = df_opady10min[(df_opady10min[0] == id) & (df_opady10min[2].str.startswith(f"{year}-{month}-{day}"))]
    #     print(filtered_opad10min)
    #     filtered_opadDobowy = df_opadDobowy[(df_opadDobowy[0] == id) & (df_opadDobowy[2].str.startswith(f"{year}-{month}-{day}"))]
    #     print(filtered_opadDobowy)
    #     filtered_wilgotnosc = df_wilgotnosc[(df_wilgotnosc[0] == id) & (df_wilgotnosc[2].str.startswith(f"{year}-{month}-{day}"))]
    #     filtered_snieg = df_snieg[(df_snieg[0] == id) & (df_snieg[2].str.startswith(f"{year}-{month}-{day}"))]
    #     opady10min = pd.Series(filtered_opad10min[3])
    #     print(opady10min.mean())
    #     opadDobowy = pd.Series(filtered_opadDobowy[3])
    #     print(opadDobowy)
    #     wilgotnosc = pd.Series(filtered_wilgotnosc[3])
    #     print(wilgotnosc.mean())
    #     snieg = pd.Series(filtered_snieg[3])
    #     return opady10min.mean(), opady10min.median(), opadDobowy, wilgotnosc.mean(), wilgotnosc.median(), snieg.mean(), snieg.median(), name
    #
    # elif dane == "wiatr":
    #     wiatr_dane = ["B00702A", "B00703A", "B00714A"]
    #
    #     df_sredpred = pd.read_csv(rf"C:\Users\krisr\OneDrive\Pulpit\PAG2\p2\{wiatr_dane[0]}_{year}_{month}.csv", sep=';', header=None)
    #     df_maxpred = pd.read_csv(rf"C:\Users\krisr\OneDrive\Pulpit\PAG2\p2\{wiatr_dane[1]}_{year}_{month}.csv", sep=';', header=None)
    #     df_maxporyw = pd.read_csv(rf"C:\Users\krisr\OneDrive\Pulpit\PAG2\p2\{wiatr_dane[2]}_{year}_{month}.csv", sep=';', header=None)
    #     df_sredpred[0] = df_sredpred[0].astype(str).str.strip()
    #     df_sredpred[2] = df_sredpred[2].astype(str).str.strip()
    #     df_maxpred[0] = df_maxpred[0].astype(str).str.strip()
    #     df_maxpred[2] = df_maxpred[2].astype(str).str.strip()
    #     df_maxporyw[0] = df_maxporyw[0].astype(str).str.strip()
    #     df_maxporyw[2] = df_maxporyw[2].astype(str).str.strip()
    #     filtered_sredpred = df_sredpred[(df_sredpred[0] == id) & (df_sredpred[2].str.startswith(f"{year}-{month}-{day}"))]
    #     filtered_maxpred = df_maxpred[(df_maxpred[0] == id) & (df_maxpred[2].str.startswith(f"{year}-{month}-{day}"))]
    #     filtered_maxporyw = df_maxporyw[(df_maxporyw[0] == id) & (df_maxporyw[2].str.startswith(f"{year}-{month}-{day}"))]
    #     sredpred = pd.Series(filtered_sredpred[3])
    #     max_maxpred = pd.Series(filtered_maxpred[3])
    #     max_maxporyw = pd.Series(filtered_maxporyw[3])
    #     return sredpred.mean(), sredpred.median(), max_maxpred.max(), max_maxporyw.max(), name

# Ustawienie rzeczy potrzebnych do działania api ze stroną
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join("static", "index.html"))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
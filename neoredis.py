
import csv
from pymongo import MongoClient
import geopandas as gpd
import hashlib
import pandas as pd
import glob
import os
import redis
from shapely.geometry import Point

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

# !!!! Tego nie dotykamy !!!!!
'''
def dms_to_dd(dms_str):
    parts = dms_str.split()
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    return degrees + (minutes / 60) + (seconds / 3600)

punkty_df = pd.read_csv("kody_stacji.csv", delimiter=";")

# # Konwersja współrzędnych z DMS na decimal degrees
punkty_df["Latitude"] = punkty_df["Szerokość geograficzna"].apply(dms_to_dd)
punkty_df["Longitude"] = punkty_df["Długość geograficzna"].apply(dms_to_dd)

for index, row in punkty_df.iterrows():
    klucz = generuj_klucz(row['Latitude'], row['Longitude'])
    wartosc = f"{row['ID']}, {row['Nazwa']}"
    r.set(klucz, wartosc)

for index, row in punkty_df.iterrows():
    klucz = generuj_klucz(row['Latitude'], row['Longitude'])
    print(r.get(klucz))

# Krok 1: Wczytaj dane powiatów z pliku SHP
powiaty_gdf = gpd.read_file("powiaty.shp")
powiaty_gdf = powiaty_gdf.to_crs("EPSG:4326")  # WGS 84

# Tworzenie obiektów Point w formacie Shapely
punkty_df["geometry"] = punkty_df.apply(
    lambda row: Point(row["Longitude"], row["Latitude"]),
    axis=1,
)

# Konwertuj DataFrame punktów na GeoDataFrame
punkty_gdf = gpd.GeoDataFrame(punkty_df, geometry="geometry", crs="EPSG:4326")

# Krok 3: Połączenie punktów z powiatami
powiaty_z_punktami = {}

for _, powiat in powiaty_gdf.iterrows():
    powiat_id = powiat["national_c"]  # Dopasuj nazwę kolumny
    punkty_w_powiecie = punkty_gdf[punkty_gdf.geometry.within(powiat.geometry)]
    wspolrzedne = [(point.geometry.x, point.geometry.y) for _, point in punkty_w_powiecie.iterrows()]
    powiaty_z_punktami[powiat_id] = wspolrzedne

for powiat_id, wspolrzedne in powiaty_z_punktami.items():
    redis_value = ";".join([f"{x},{y}" for x, y in wspolrzedne])
    r.set(powiat_id, redis_value)
'''


# wpisujesz numer teryt powiatu, który wybrałeś
TERYT = "0226"

# pobieranie stringa z bazy
points_str = r.get(TERYT)

# robienie listy punktów
points_list = [tuple(map(float, point.split(','))) for point in points_str.split(';')]
print(points_list)
# przykładowy wynik: [(15.747499999999999, 51.09055555555556), (15.88888888888889, 51.01694444444444), (15.88888888888889, 51.01694444444444)]



# TUTAJ wpisujesz punkt, który kliknąłeś
index = 0
selected_point_latitude = points_list[index][1]
selected_point_longitude = points_list[index][0]

print("Długość geograficzna pierwszego punktu:", selected_point_latitude)
print("Długość geograficzna pierwszego punktu:", selected_point_longitude)

# pobierasz kod i nazwe stacji. NAJPIERW LAT, POTEM LON !!!!!!
kod_str = r.get(generuj_klucz(selected_point_latitude, selected_point_longitude))
kod_list = kod_str.split(', ')

#ID stacji
id = kod_list[0]

#Nazwa stacji
name = kod_list[1]

print(id, name)
import redis
import csv
from pymongo import MongoClient
import geopandas as gpd
import hashlib
import pandas as pd
import glob
import os

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


# df = pd.read_csv("kody_stacji.csv", sep=';', header=0, names=['Lp', 'kod_stacji', 'nazwa_stacji', 'szerokosc', 'dlugosc', 'wysokosc'])

# print(df.head(50))

# for index, row in df.iterrows():
#     klucz = generuj_klucz(row['szerokosc'], row['dlugosc'])
#     wartosc = f"{row}"
#     r.set(klucz, wartosc)

print(r.get(generuj_klucz('49 59 44', '18 55 09')))

print("DONE")

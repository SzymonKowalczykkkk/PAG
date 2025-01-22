
import csv
import geopandas as gpd
import hashlib
import pandas as pd
import glob
import os
import redis

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


df = pd.read_csv(r"C:\Semestr_5\PAG\Projekt-blok-2\kody_stacji.csv", sep=';', header=0, names=['kod_stacji', 'miejscowosc', 'nazwa_stacji', 'szerokosc', 'dlugosc', 'wysokosc'])

# print(df.head(50))

# for index, row in df.iterrows():
#     klucz = generuj_klucz(row['szerokosc'], row['dlugosc'])
#     wartosc = f"{row['kod_stacji']}, {row['nazwa_stacji']}"
#     r.set(klucz, wartosc)   

wynik = r.get(generuj_klucz('49 59 44', '18 55 09'))
wynik = wynik.split(", ")


print(f"id: " + wynik[0])
print(f"name: " + wynik[1])

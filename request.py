import requests
import json
import pandas as pd
import geopandas as gpd
import zipfile
import string

# Funkcja automatycznie pobierające dane pogodowe
def data_request(month, year) -> pd.DataFrame:
    base = "https://dane.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo"
    link = f"{base}/{year}/Meteo_{year}-{month}.zip"
    print(link)
    request = requests.get(link)
    print(request.status_code)

    #download the file
    with open(f"Meteo_{year}-{month}.zip", "wb") as file:
        file.write(request.content)

    #unzip the file
    with zipfile.ZipFile(f"Meteo_{year}-{month}.zip", "r") as zip_ref:
        zip_ref.extractall(f"Meteo_{year}-{month}")

    kierunek_wiatru = pd.read_csv(string.startswith('B00701A'))
    temperatura_powietrza = pd.read_csv(string.startswith('B00300S'))
    temperatura_gruntu = pd.read_csv(string.startswith('B00305A'))
    srednia_predkosc_wiatru = pd.read_csv(string.startswith('B00702A'))
    predkosc_maksymalna = pd.read_csv(string.startswith('B00703A'))
    suma_opadu_10min = pd.read_csv(string.startswith('B00608S'))
    suma_opadu_dobowego = pd.read_csv(string.startswith('B00604S'))
    suma_opadu_godzinowego = pd.read_csv(string.startswith('B00606S'))
    wilgotnosc_wzgledna_powietrza = pd.read_csv(string.startswith('B00802A'))
    najwiekszy_poryw_wiatru = pd.read_csv(string.startswith('B00714A'))

    return kierunek_wiatru, temperatura_powietrza, temperatura_gruntu, srednia_predkosc_wiatru, predkosc_maksymalna, suma_opadu_10min, suma_opadu_dobowego, suma_opadu_godzinowego, wilgotnosc_wzgledna_powietrza, najwiekszy_poryw_wiatru

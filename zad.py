import pandas
import geopandas
import matplotlib.pyplot as plt
import numpy as np
import astral
import sys
sys.path.append(r'Dane')
import os
os.chdir(r'Dane')
from request import data_request
import tkinter as tk
import folium 

if __name__ == '__main__':
    powiaty = geopandas.read_file('powiaty.shp')
    wojewodztwa = geopandas.read_file('woj.shp')
    dane = geopandas.read_file('effacility.geojson')

    window = tk.Tk()
    window.title("Weather data")
    window.geometry('400x200')  
    window.resizable(False, False)
    window.configure(background='grey')

    #data = data_request(1, 2020)

#uwtórz stronę internetową wyświetlającą wojweództwa na mapie jak się przybliżyć to powiaty i lokalizacje stacji pogodowych
#dodaj przyciski do zmiany miesiąca i roku
#dodaj przycisk do pobrania danych

    m = folium.Map(location=[52, 19], zoom_start=6)
    folium.GeoJson(wojewodztwa).add_to(m)
    folium.GeoJson(powiaty).add_to(m)
    folium.GeoJson(dane).add_to(m)

    m.save('map.html')
    os.system('map.html')

    window.mainloop()
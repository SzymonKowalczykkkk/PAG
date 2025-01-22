import pandas
import geopandas
import matplotlib.pyplot as plt
import numpy as np
import astral
import sys
import numpy as np
sys.path.append(r'Dane')
import os
os.chdir(r'Dane')
from request import data_request
import tkinter as tk

powiaty = geopandas.read_file('powiaty.shp')
wojewodztwa = geopandas.read_file('woj.shp')

# get national_c from atributes from powiat shapefile
powiaty_teryt = powiaty['national_c', 'name']
wojewodztwa_teryt = wojewodztwa['national_c', 'name']

print(powiaty_teryt)
print(wojewodztwa_teryt)

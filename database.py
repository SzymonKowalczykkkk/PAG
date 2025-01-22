import redis
import csv
from pymongo import MongoClient
import geopandas as gpd

# r = redis.Redis(
#     host='redis-14467.c328.europe-west3-1.gce.redns.redis-cloud.com',
#     port=14467,
#     decode_responses=True,
#     username="default",
#     password="8xmJmdTFc0xMn8lutuzYqDMXRShMoyGP",
# )


# # with open("kody_stacji.csv", encoding='utf-8') as csvfile:
# #     for row in csv.DictReader(csvfile, delimiter=';'):
# #         key = row['ID']
# #         value = row['Nazwa'] + ";" + row['Rzeka'] + ";" + row['Szerokość geograficzna'] + ";" + row['Długość geograficzna'] + ";" + row['Wysokość n.p.m.']
# #         r.set(key, value)

# print(r.get('354160105'))


# uri = "mongodb+srv://szymon:PAG2@cluster0.gymzp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(uri)

# try:
#     database = client.get_database("sample_mflix")
    
#     collection_list = database.list_collection_names()
    
#     # drop collections
#     for c in collection_list:
#         collection = database.get_collection(c)
#         collection.drop()

    
#     client.close()

# except Exception as e:
#     raise Exception("Unable to find the document due to the following error: ", e)

powiaty = gpd.read_file(r"C:\Semestr_5\PAG\wys\Dane\powiaty.shp")

stacje = gpd.read_file("kody_stacji.csv", delimiter=';')
print("Nazwy kolumn:", stacje.columns)

# stacje = gpd.GeoDataFrame(stacje, geometry=gpd.points_from_xy(stacje['Długość geograficzna'], stacje['Szerokość geograficzna']))

# przypisania = gpd.sjoin(stacje, powiaty, how='left', op='within')

# print(przypisania)
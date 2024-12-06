import redis
import csv

r = redis.Redis(
    host='redis-14467.c328.europe-west3-1.gce.redns.redis-cloud.com',
    port=14467,
    decode_responses=True,
    username="default",
    password="8xmJmdTFc0xMn8lutuzYqDMXRShMoyGP",
)


# with open("kody_stacji.csv", encoding='utf-8') as csvfile:
#     for row in csv.DictReader(csvfile, delimiter=';'):
#         key = row['ID']
#         value = row['Nazwa'] + ";" + row['Rzeka'] + ";" + row['Szerokość geograficzna'] + ";" + row['Długość geograficzna'] + ";" + row['Wysokość n.p.m.']
#         r.set(key, value)

print(r.get('354160105'))


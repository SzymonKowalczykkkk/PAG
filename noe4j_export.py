from neo4j import GraphDatabase
import xml.etree.ElementTree as ET

file_path = r"C:\Users\krisr\OneDrive\Pulpit\PAG2\p1\warsaw"

nodes_data = []

with open(file_path, 'r', encoding='utf-8') as file:
    tree = ET.parse(file)
    root = tree.getroot()

ns = {"": "http://graphml.graphdrawing.org/xmlns"}

# Iterate through the nodes and extract relevant data
for node in root.findall(".//node", namespaces=ns):
    node_id = node.get("id")
    d4 = node.find(".//data[@key='d4']", namespaces=ns)
    d5 = node.find(".//data[@key='d5']", namespaces=ns)
    d6 = node.find(".//data[@key='d6']", namespaces=ns)

    # Add to the array if all values are found
    if node_id and d4 is not None and d5 is not None and d6 is not None:
        nodes_data.append({
            "id": node_id,
            "lat": d4.text,
            "lon": d5.text,
            "direction": d6.text,
        })

query = "CREATE "

for node in nodes_data:
    query = query + "(:node {id:"+node["id"]+", lat:"+node["lat"]+", lon:"+node["lon"]+", direction:"+node["direction"]+"), "
query = query[:-2]+"};"
print(query)

user = "neo4j"
password = "12345321"
driver = GraphDatabase.driver("bolt://localhost:7687", auth=(user, password))
session = driver.session()

session.run(query)

session.close

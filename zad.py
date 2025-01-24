import pandas
import geopandas
import matplotlib.pyplot as plt
import numpy as np
from neo4j import GraphDatabase
import geojson
import tkinter as tk
from tkinter import ttk

# Upewnij się, że używasz poprawnych danych uwierzytelniających
username = "neo4j"
password = "19MhiW09!"  # Zmień na swoje hasło

driver = GraphDatabase.driver("bolt://localhost:7687", auth=(username, password))
session = driver.session()

source_x = 20.9963881
source_y = 52.1652338
target_x = 20.9993645
target_y = 52.1569005

# Tworzenie grafu
create_graph_query = """
MATCH (source:Nodes)-[r:RELATED]->(target:Nodes)
RETURN gds.graph.project(
  'NavGraph25',
  source,
  target,
  {
    sourceNodeProperties: source { .x, .y },
    targetNodeProperties: target { .x, .y },
    relationshipProperties: r { .length }
  }
)
"""
# session.run(create_graph_query)

# Wykonywanie zapytania A* do znalezienia najkrótszej ścieżki
shortest_path_query = f"""
MATCH (source {{x: {source_x}, y: {source_y}}}), (target {{x: {target_x}, y: {target_y}}})
CALL gds.shortestPath.astar.stream('NavGraph25', {{
    sourceNode: source,
    targetNode: target,
    latitudeProperty: 'x',
    longitudeProperty: 'y',
    relationshipWeightProperty: 'length'
}})
YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
RETURN
index,
gds.util.asNode(sourceNode).name AS sourceNodeName,
gds.util.asNode(targetNode).name AS targetNodeName,
totalCost,
[nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,
costs,
nodes(path) as path
ORDER BY index
"""
result = session.run(shortest_path_query)

# Przetwarzanie wyników i zapisywanie do GeoJSON
features = []
for record in result:
    path = record['path']
    coordinates = [(node['x'], node['y']) for node in path]
    feature = geojson.Feature(
        geometry=geojson.LineString(coordinates),
        properties={
            "index": record['index'],
            "sourceNodeName": record['sourceNodeName'],
            "targetNodeName": record['targetNodeName'],
            "totalCost": record['totalCost'],
            "nodeNames": record['nodeNames'],
            "costs": record['costs']
        }
    )
    features.append(feature)

feature_collection = geojson.FeatureCollection(features)

with open('shortest_path.geojson', 'w') as f:
    geojson.dump(feature_collection, f, indent=2)

session.close()

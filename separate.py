import json
import os
import unicodedata

def polish_remover(name):
        #usuwanie polskich znakow z nazwy
    name = unicodedata.normalize('NFD', name)
    name = ''.join([c for c in name if unicodedata.category(c) != 'Mn'])
    name = name.replace(' ', '_').lower()
    print(name)
    return name

def separate_geojson(in_file, output_directory):
        #rozdzielenie geojsona na osobne geojsony
    with open(in_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for feature in data['features']:
        woj_name = feature['properties']['name']
        
        sanitized_woj_name = polish_remover(woj_name)

        output_geojson_path = os.path.join(output_directory, f"{sanitized_woj_name}.geojson")

        feature_collection = {
            "type": "FeatureCollection",
            "name": sanitized_woj_name,
            "features": [feature]
        }
        

        with open(output_geojson_path, 'w', encoding='utf-8') as output_file:
            json.dump(feature_collection, output_file, ensure_ascii=False, indent=4)


def main():
    woj_file = r"path_to_geojson"
    output_directory = r"output_path"
    separate_geojson(woj_file, output_directory)

if __name__ == "__main__":
    main()
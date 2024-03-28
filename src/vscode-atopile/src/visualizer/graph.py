from graphviz import Graph

import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(current_dir, 'data.json')

def open_data():
    # Open the data.json file and load its contents
    with open(data_file_path, 'r') as file:
        data = json.load(file)
    return data

# Create a new undirected graph
g = Graph('G', filename='undirected_graph.gv', engine='neato')

data = open_data()

for link in data["ios"]["links"]:
    g.edge(link["source"]["block"], link["target"]["block"])


# Optional: Add more attributes to style the graph
g.attr(overlap='false', splines='true')

# Render the graph to an SVG file
g.render(format='svg', view=True)

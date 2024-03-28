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

data = open_data()

for module in data:
    # Create a new undirected graph
    g = Graph('G', filename=f"{module}.gv", engine='neato')

    for block in data[module]["blocks"]:
        if block["type"] == "interface":
            g.node(block["name"], shape='point', style='filled', fillcolor='blue', xlabel=f"<<font point-size='8'>{block['instance_of']}, {block['name']}</font>>")
        elif block["type"] == "module":
            g.node(block["name"], shape='box', style='filled', fillcolor='lightgreen', label=f"<{block['instance_of']}<br/><b>{block['name']}</b>>")
        elif block["type"] == "component":
            g.node(block["name"], shape='box', style='filled', fillcolor='lightyellow', label=f"<{block['instance_of']}<br/><b>{block['name']}</b>>")
        else:
            g.node(block["name"], shape='point', style='filled', fillcolor='gray', xlabel=f"<<font point-size='8'>{block['instance_of']}, {block['name']}</font>>")

    for link in data[module]["links"]:
        g.edge(link["source"]["block"], link["target"]["block"])


    # Optional: Add more attributes to style the graph
    g.attr(overlap='false', splines='true')

    # Render the graph to an SVG file
    g.render(format='svg', view=True)

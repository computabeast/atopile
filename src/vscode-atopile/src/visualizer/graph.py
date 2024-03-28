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
            g.node(block["name"], shape='point', style='filled', fillcolor='blue', xlabel=f"<<font point-size='8'><i>{block['instance_of']}</i><br/><b>{block['name']}</b></font>>")
        elif block["type"] == "module":
            g.node(block["name"], shape='box', style='filled', fillcolor='lightgreen', label=f"<<font point-size='8'><i>{block['instance_of']}</i></font><font point-size='10'><br/><b>{block['name']}</b></font>>")
        elif block["type"] == "component":
            g.node(block["name"], shape='box', style='filled', fillcolor='lightyellow', label=f"<<font point-size='8'><i>{block['instance_of']}</i></font><font point-size='10'><br/><b>{block['name']}</b></font>>")
        else:
            g.node(block["name"], shape='point', style='filled', fillcolor='gray', xlabel=f"<<b><font point-size='8'>{block['name']}</font></b>>")

    for link in data[module]["links"]:
        if link["type"] == "signal":
            g.edge(f"{link['source']['block']}", f"{link['target']['block']}", style='dashed')
        else:
            g.edge(f"{link['source']['block']}", f"{link['target']['block']}")


    # Optional: Add more attributes to style the graph
    g.attr(overlap='false', splines='true')

    # Render the graph to an SVG file
    g.render(format='svg', view=True)

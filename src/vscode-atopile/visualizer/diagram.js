var namespace = joint.shapes;

const { shapes, util, dia, anchors } = joint;

let settings_dict = {
    common: {
        backgroundColor: 'rgba(224, 233, 227, 0.3)',
        gridSize: 15,
        parentPadding: 45,
        fontFamily: "monospace",
    },
    component : {
        strokeWidth: 2,
        fontSize: 8,
        fontWeight: "bold",
        defaultWidth: 60,
        portPitch: 15,
        defaultHeight: 50,
        labelHorizontalMargin: 15,
        labelVerticalMargin: 15,
        titleMargin: 5,
        portLabelToBorderGap: 3,
        pin: {
            fontSize: 8,
            fontWeight: "normal",
        },
    },
    block : {
        strokeWidth: 2,
        boxRadius: 5,
        strokeDasharray: '4,4',
        label: {
            fontSize: 8,
            fontWeight: "bold",
        }
    },
    link: {
        strokeWidth: 1,
        color: "blue"
    },
    stubs: {
        fontSize: 8,
    },
    interface: {
        fontSize: 8,
        color: "blue",
        strokeWidth: 3,
    }
}

class AtoElement extends dia.Element {
    defaults() {
        return {
            ...super.defaults,
            type: "AtoComponent",
            attrs: {
                body: {
                    fill: "white",
                    z: 10,
                    stroke: "black",
                    strokeWidth: settings_dict["component"]["strokeWidth"],
                    width: "calc(w)",
                    height: "calc(h)",
                    rx: 5,
                    ry: 5
                },
                label: {
                    text: "Component",
                    fill: "black",
                    fontSize: settings_dict["component"]["fontSize"],
                    fontWeight: settings_dict["component"]["fontWeight"],
                    textVerticalAnchor: "middle",
                    textAnchor: "middle",
                    fontFamily: settings_dict["common"]["fontFamily"],
                    x: "calc(w/2)",
                    y: "calc(h/2)"
                }
            }
        };
    }

    preinitialize() {
        this.markup = util.svg`
            <rect @selector="body" />
            <text @selector="label" />
        `;
    }
}

const cellNamespace = {
    ...shapes,
    AtoElement
};

var data = {};
fetch('data.json')
    .then(response => response.json())
    .then(jsonData => {
        data = jsonData;
        console.log("Loaded data:", data); // Log the loaded data
        addRectangles(data); // Call the function to add rectangles

        addLinks(data); // Call the function to add links
    })
    .catch(error => console.error('Error loading data.json:', error));

function addRectangles(data) {
    if (data.blocks && Array.isArray(data.blocks)) {
        data.blocks.forEach((module, index) => {
            var rect = new AtoElement(
                {
                    id: module,
                    instance_name: module,
                    size: {
                        width: 10,
                        height: 10
                    },
                    attrs: {
                        label: {
                            text: module,
                        }
                    },
                }
            );
            rect.position(100, 30 + (50 * index)); // Adjust position for each rectangle
            rect.resize(100, 40);
            console.log(`Creating rectangle for module ${module}`);
            rect.addTo(graph);
        });
    } else {
        console.error('data.modules is undefined or not an array');
    }
}

function addLink(source_block_id, target_block_id) {
    console.log(`Creating link from ${source_block_id} to ${target_block_id}`);
    var added_link = new shapes.standard.Link({
        source: {id: source_block_id},
        target: {id: target_block_id}
    });
    added_link.attr({
        line: {
            'stroke': settings_dict['link']['color'],
            'stroke-width': 1,
            targetMarker: { 'type': 'none' },
        },
        z: 0
    });
    // added_link.router('manhattan', {
    //     perpendicular: true,
    //     step: settings_dict['common']['gridSize'] / 2,
    // });

    return added_link;
}

function addLinks(data) {
    if (data.links && Array.isArray(data.links)) {
        console.log("All cells in the graph:", graph.getCells());
        data.links.forEach(link => {

            console.log(`Creating link from ${link.from} to ${link.to}`);

            // if (sourceModule && targetModule) {
            var link = addLink(link.source.block, link.target.block)
            link.addTo(graph);
            // } else {
            //     console.error('One of the modules in the link is undefined:', link);
            // }
        });
    } else {
        console.error('data.links is undefined or not an array');
    }
}


var graph = new joint.dia.Graph({}, { cellNamespace: namespace });

var paper = new joint.dia.Paper({
    el: document.getElementById('myholder'),
    model: graph,
    width: 600,
    height: 600,
    gridSize: 1,
    cellViewNamespace: namespace
});

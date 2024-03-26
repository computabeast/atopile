var namespace = joint.shapes;

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
    if (data.modules && Array.isArray(data.modules)) {
        data.modules.forEach((module, index) => {
            var rect = new joint.shapes.standard.Rectangle();
            rect.position(100, 30 + (50 * index)); // Adjust position for each rectangle
            rect.resize(100, 40);
            rect.id = module;
            rect.attr({
                body: {
                    fill: 'blue'
                },
                label: {
                    text: module.split('::').pop(),
                    fill: 'white'
                }
            });
            rect.addTo(graph);
        });
    } else {
        console.error('data.modules is undefined or not an array');
    }
}

function addLinks(data) {
    if (data.links && Array.isArray(data.links)) {
        console.log("All cells in the graph:", graph.getCells());
        data.links.forEach(link => {
            var sourceModule = graph.getCell(link.from);
            var targetModule = graph.getCell(link.to);

            console.log(`Creating link from ${link.from} to ${link.to}`);

            // if (sourceModule && targetModule) {
            var link = new joint.shapes.standard.Link();
            link.source({ id: sourceModule.id });
            link.target({ id: targetModule.id });
            link.attr({
                line: {
                    stroke: 'black',
                    strokeWidth: 2,
                    targetMarker: {
                        'type': 'path',
                        'd': 'M 10 -5 0 0 10 5 Z'
                    }
                }
            });
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

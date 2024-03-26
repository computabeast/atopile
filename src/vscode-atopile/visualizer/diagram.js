var namespace = joint.shapes;

var data = {};
fetch('data.json')
    .then(response => response.json())
    .then(jsonData => {
        data = jsonData;
        console.log("Loaded data:", data); // Log the loaded data
    })
    .catch(error => console.error('Error loading data.json:', error));

// console.log("Number of modules:", data.modules.length);
// console.log("Number of links:", data.links.length);

var graph = new joint.dia.Graph({}, { cellNamespace: namespace });

var paper = new joint.dia.Paper({
    el: document.getElementById('myholder'),
    model: graph,
    width: 600,
    height: 600,
    gridSize: 1,
    cellViewNamespace: namespace
});

data.modules.forEach((module, index) => {
    var rect = new joint.shapes.standard.Rectangle();
    rect.position(100, 30 + (50 * index)); // Adjust position for each rectangle
    rect.resize(100, 40);
    rect.attr({
        body: {
            fill: 'blue'
        },
        label: {
            text: module,
            fill: 'white'
        }
    });
    rect.addTo(graph);
});

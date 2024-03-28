async function loadJsonAsDict() {
    const response = await fetch('http://127.0.0.1:5000/data');
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

function loadNodes(data) {
    return data["ios"]["blocks"].map(block => ({
        id: block["name"]
    }));
}

function loadLinks(data) {
    return data["ios"]["links"].map(block => ({
        source: block["source"]["block"], target: block["target"]["block"]
    }));
}

async function initializeGraph() {

    const data = await loadJsonAsDict();

    const nodes = loadNodes(data);
    const links = loadLinks(data);
    // const links = [{ source: "ios", target: "micro" }]
    // const links = Array.from({ length: nodes.length }, () => ({
    //     source: nodes[Math.floor(Math.random() * nodes.length)].id,
    //     target: nodes[Math.floor(Math.random() * nodes.length)].id,
    // }));

    const svg = d3.select("svg");
    const width = +svg.attr("width");
    const height = +svg.attr("height");

    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });

    svg.call(zoom);

    const g = svg.append("g");

    const forceNode = d3.forceManyBody().strength(-1000);
    const forceLink = d3.forceLink(links).id(d => d.id);
    // if (nodeStrength !== undefined) forceNode.strength(nodeStrength);
    // if (linkStrength !== undefined) forceLink.strength(linkStrength);

    const simulation = d3.forceSimulation(nodes)
        .force("link", forceLink)
        .force("charge", forceNode)
        // .force("x", d3.forceX())
        // .force("y", d3.forceY())
        .force("center", d3.forceCenter(width / 2, height / 2).strength(0.1));

    const link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .join("line");

    const node = g.append("g")
        .attr("class", "nodes")
        .selectAll("rect")
        .data(nodes)
        .join("rect")
        .attr("width", 100)
        .attr("height", 50)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("fill", "#aaa")
        .call(drag(simulation));

    const text = g.append("g")
        .attr("class", "texts")
        .selectAll("text")
        .data(nodes)
        .join("text")
        .attr("x", d => d.x + 50)
        .attr("y", d => d.y + 25)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .text(d => d.id);

    function drag(simulation) {
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }

    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x + 50)
            .attr("y1", d => d.source.y + 25)
            .attr("x2", d => d.target.x + 50)
            .attr("y2", d => d.target.y + 25);

        node
            .attr("x", d => d.x = Math.max(0, Math.min(width - 100, d.x)))
            .attr("y", d => d.y = Math.max(0, Math.min(height - 50, d.y)));

        text
            .attr("x", d => d.x + 50)
            .attr("y", d => d.y + 25);
    });
}

initializeGraph();
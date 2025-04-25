console.log('Graph: Script started');

if (typeof d3 === 'undefined') {
  console.error('Graph: D3.js not loaded');
} else {
  console.log('Graph: D3.js loaded successfully');
}

// Add error handler
window.onerror = function(msg, url, lineNo, columnNo, error) {
  console.error('Graph: Iframe Error:', msg, 'at', url, 'line', lineNo, 'column', columnNo, 'Error object:', error);
  document.body.innerHTML = '<div style="color: red; padding: 20px;">Iframe Error: ' + msg + '</div>';
  return false;
};

document.addEventListener('DOMContentLoaded', () => {
  console.log('Graph: DOMContentLoaded');
});

// Listen for graph data from parent
window.addEventListener('message', (event) => {
  console.log('Graph: Received message:', event.data);
  if (event.data.type === 'renderGraph' && event.data.graphData) {
    console.log('Graph: Initializing graph with data:', event.data.graphData);
    initializeGraphWithData(event.data.graphData);
  } else {
    console.error('Graph: Invalid message format or missing graph data');
  }
});

function initializeGraphWithData(data) {
  console.log('Graph: initializeGraphWithData called with:', data);
  if (!data || !data.nodes || !data.links) {
    console.error('Graph: Invalid graph data');
    document.getElementById('loading').innerText = 'Error: Invalid graph data';
    return;
  }

  const container = document.getElementById('container');
  if (!container) {
    console.error('Graph: Container not found');
    document.body.innerHTML = '<div style="color: red; padding: 20px;">Error: Container not found</div>';
    return;
  }

  console.log('Graph: Setting up SVG');
  const width = container.clientWidth;
  const height = container.clientHeight;

  const svg = d3.select('#container')
    .append('svg')
    .attr('width', '100%')
    .attr('height', '100%')
    .call(d3.zoom().on('zoom', function (event) {
      svg.attr('transform', event.transform);
    }))
    .append('g');

  svg.append('defs').append('marker')
    .attr('id', 'arrow')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 15)
    .attr('refY', 0)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('fill', '#999')
    .attr('d', 'M0,-5L10,0L0,5');

  console.log('Graph: SVG setup complete');

  const simulation = d3.forceSimulation(data.nodes)
    .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2));

  const link = svg.selectAll('.link')
    .data(data.links)
    .enter()
    .append('line')
    .attr('class', 'link');

  const node = svg.selectAll('.node')
    .data(data.nodes)
    .enter()
    .append('g')
    .attr('class', 'node')
    .call(d3.drag()
      .on('start', dragStarted)
      .on('drag', dragged)
      .on('end', dragEnded));

  node.append('circle')
    .attr('r', 5)
    .attr('fill', '#69b3a2');

  node.append('text')
    .attr('dx', 12)
    .attr('dy', '.35em')
    .attr('fill', '#000000') // Node name color is black
    .text(d => d.label);

  console.log('Graph: Nodes and links appended');

  const tooltip = d3.select('.tooltip');

  node.on('mouseover', function (event, d) {
    tooltip.transition().duration(200).style('opacity', .9);
    tooltip.html(d.label)
      .style('left', (event.pageX + 10) + 'px')
      .style('top', (event.pageY - 28) + 'px');
  })
  .on('mouseout', function () {
    tooltip.transition().duration(500).style('opacity', 0);
  });

  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

    node
      .attr('transform', d => `translate(${d.x},${d.y})`);
  });

  function dragStarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragEnded(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  d3.select('#search-btn').on('click', () => {
    const searchTerm = document.getElementById('search').value.toLowerCase();
    node.selectAll('circle')
      .attr('fill', d => d.label.toLowerCase().includes(searchTerm) ? '#ff0000' : '#69b3a2');
  });

  d3.select('#zoom-in').on('click', () => {
    svg.transition().call(d3.zoom().scaleBy, 1.2);
  });

  d3.select('#zoom-out').on('click', () => {
    svg.transition().call(d3.zoom().scaleBy, 0.8);
  });

  d3.select('#reset').on('click', () => {
    svg.transition().call(d3.zoom().transform, d3.zoomIdentity);
  });

  let labelsVisible = true;
  d3.select('#toggle-labels').on('click', () => {
    labelsVisible = !labelsVisible;
    node.selectAll('text').style('display', labelsVisible ? 'block' : 'none');
  });

  d3.select('#export-svg').on('click', () => {
    const svgElement = document.querySelector('svg');
    const serializer = new XMLSerializer();
    const source = serializer.serializeToString(svgElement);
    const blob = new Blob(['<?xml version="1.0" standalone="no"?>\r\n' + source], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'graph.svg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  });

  document.getElementById('node-count').innerText = data.nodes.length;
  document.getElementById('edge-count').innerText = data.links.length;

  document.getElementById('loading').remove();
  console.log('Graph: Graph rendering complete');
}
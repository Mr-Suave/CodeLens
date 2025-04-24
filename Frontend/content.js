/* content.js */
function isGitHubRepoPage() {
  return /^https:\/\/github\.com\/[^\/]+\/[^\/]+(\/)?$/.test(window.location.href);
}

function getRepoInfo() {
  const pathParts = window.location.pathname.split('/').filter(part => part.length > 0);
  if (pathParts.length >= 2) {
    return {
      owner: pathParts[0],
      repo: pathParts[1]
    };
  }
  return null;
}

function createCodeLensButton() {
  const button = document.createElement('div');
  button.id = 'codelens-btn';
  button.innerText = 'CodeLens';
  document.body.appendChild(button);
  
  button.onclick = () => {
    const overlay = document.createElement('div');
    overlay.id = 'codelens-overlay';
    button.style.display = 'none';

    const title = document.createElement('h2');
    title.className = 'codelens-title';
    title.innerText = 'CodeLens';
    overlay.appendChild(title);

    const subtitle = document.createElement('h3');
    subtitle.className = 'codelens-subtitle';
    subtitle.innerText = 'Documentation making just got easier!';
    overlay.appendChild(subtitle);
    
    // First Button: Documentation
    const docBtn = document.createElement('button');
    docBtn.className = 'overlay-btn';
    docBtn.innerText = 'View Documentation For the Repository';
    docBtn.addEventListener('click', () => {
      // Placeholder for documentation function
      // alert('Documentation button clicked!');
    });
    overlay.appendChild(docBtn);

    // Second Button: Commit Messages Graph
    const graphBtn = document.createElement('button');
    graphBtn.className = 'overlay-btn';
    graphBtn.innerText = 'View Commit Messages Graph';
    graphBtn.addEventListener('click', showFunctionCallGraph); // Assuming this function exists
    overlay.appendChild(graphBtn);

    // Third Button: Commit History Graph
    const historyBtn = document.createElement('button');
    historyBtn.className = 'overlay-btn';
    historyBtn.innerText = 'View Commit History Graph';
    historyBtn.addEventListener('click', () => {
      const img = document.createElement('img');
      img.src = '../commit_graph.png'; // Adjust path if needed
      img.alt = 'Commit History Graph';
      img.style.maxWidth = '90%';
      img.style.marginTop = '20px';
      overlay.appendChild(img);
    });
    overlay.appendChild(historyBtn);

    document.body.appendChild(overlay);

    // Close overlay when clicking outside the overlay
    function handleOutsideClick(e) {
      const rect = overlay.getBoundingClientRect();
      if (e.clientX < rect.left) {
        overlay.remove();
        button.style.display = 'block';
        document.removeEventListener('click', handleOutsideClick);
      }
    }

    document.addEventListener('click', handleOutsideClick);
  };
}



function showFunctionCallGraph() {
  // Get repository information
  const repoInfo = getRepoInfo();
  if (!repoInfo) {
    alert('Could not determine repository information.');
    return;
  }

  // Remove existing graph container if present
  let graphContainer = document.getElementById('codelens-graph-container');
  if (graphContainer) {
    graphContainer.remove();
  }

  // Create a new container for the graph
  graphContainer = document.createElement('div');
  graphContainer.id = 'codelens-graph-container';
  graphContainer.style.position = 'fixed';
  graphContainer.style.top = '0';
  graphContainer.style.right = '0';
  graphContainer.style.width = '50vw';
  graphContainer.style.height = '100vh';
  graphContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
  graphContainer.style.zIndex = '9998';
  graphContainer.style.padding = '20px';
  graphContainer.style.overflow = 'auto';
  
  document.body.appendChild(graphContainer);

  // Add a close button
  const closeButton = document.createElement('div');
  closeButton.style.position = 'absolute';
  closeButton.style.top = '20px';
  closeButton.style.right = '20px';
  closeButton.style.color = 'white';
  closeButton.style.fontSize = '24px';
  closeButton.style.cursor = 'pointer';
  closeButton.innerText = '✕';
  closeButton.onclick = () => {
    graphContainer.remove();
  };
  graphContainer.appendChild(closeButton);

  // Add loading indicator
  const loadingIndicator = document.createElement('div');
  loadingIndicator.style.color = 'white';
  loadingIndicator.style.textAlign = 'center';
  loadingIndicator.style.marginTop = '50px';
  loadingIndicator.innerText = 'Searching for function_list.txt in repository...';
  graphContainer.appendChild(loadingIndicator);

  // Try to find function_list.txt in the repository
  fetchFunctionList(repoInfo)
    .then(functionListContent => {
      // If we got the function list, render the graph
      renderFunctionCallGraph(graphContainer, functionListContent);
    })
    .catch(error => {
      // If we couldn't find the function list, show error message
      console.error('Error fetching function list:', error);
      graphContainer.innerHTML = ''; // Clear loading indicator
      graphContainer.appendChild(closeButton);
      
      const errorMessage = document.createElement('div');
      errorMessage.style.color = 'white';
      errorMessage.style.textAlign = 'center';
      errorMessage.style.marginTop = '50px';
      errorMessage.style.padding = '20px';
      errorMessage.innerHTML = `
        <h2>Graph Not Available</h2>
        <p>Repo owner did not generate function call graph for this repository.</p>
        <p>To enable this feature, the repository needs to include a function_list.txt file in its root directory.</p>
      `;
      graphContainer.appendChild(errorMessage);
    });
}

async function fetchFunctionList(repoInfo) {
  // First, try to fetch function_list.txt from the root of the repo
  const url = `https://raw.githubusercontent.com/${repoInfo.owner}/${repoInfo.repo}/main/function_list.txt`;
  
  try {
    const response = await fetch(url);
    if (response.ok) {
      return await response.text();
    }
    
    // If not found in main branch, try master branch
    const masterUrl = `https://raw.githubusercontent.com/${repoInfo.owner}/${repoInfo.repo}/master/function_list.txt`;
    const masterResponse = await fetch(masterUrl);
    if (masterResponse.ok) {
      return await masterResponse.text();
    }
    
    throw new Error('function_list.txt not found in repository');
  } catch (error) {
    throw error;
  }
}

function renderFunctionCallGraph(container, functionListContent) {
  // Clear container content
  container.innerHTML = '';
  
  // Create the iframe for the graph
  const graphFrame = document.createElement('iframe');
  graphFrame.id = 'function-graph-frame';
  graphFrame.style.width = '100%';
  graphFrame.style.height = '100%';
  graphFrame.style.border = 'none';
  container.appendChild(graphFrame);
  
  // When the iframe loads, initialize the D3 graph
  graphFrame.onload = () => {
    const doc = graphFrame.contentDocument || graphFrame.contentWindow.document;
    
    // Initialize the graph with the fetched function list or sample data
    if (functionListContent) {
      const graphData = parseAndPrepareFunctionList(functionListContent);
      initializeGraphInIframe(doc, graphData);
    } else {
      // Use sample data
      const sampleData = createSampleGraphData();
      initializeGraphInIframe(doc, sampleData);
    }
  };
  
  // Set the content of the iframe
  const graphHTML = createGraphHTML();
  const blob = new Blob([graphHTML], { type: 'text/html' });
  graphFrame.src = URL.createObjectURL(blob);
}

function parseAndPrepareFunctionList(content) {
  const nodes = new Map();
  const links = [];
  
  const lines = content.split('\n');
  let inCallGraph = false;
  
  for (const line of lines) {
    if (line.includes('=== FUNCTION CALL GRAPH ===')) {
      inCallGraph = true;
      continue;
    }
    
    if (inCallGraph && line.includes('-->')) {
      const [source, targetsStr] = line.split('-->').map(s => s.trim());
      
      if (!nodes.has(source)) {
        nodes.set(source, { id: source, label: source });
      }
      
      if (targetsStr && targetsStr.length > 0) {
        const targets = targetsStr.split(',').map(t => t.trim());
        for (const target of targets) {
          if (target && !target.includes('...')) {
            if (!nodes.has(target)) {
              nodes.set(target, { id: target, label: target });
            }
            links.push({ source, target });
          }
        }
      }
    }
  }
  
  return {
    nodes: Array.from(nodes.values()),
    links
  };
}

function createSampleGraphData() {
  return {
    nodes: [
      { id: "main.py::main", label: "main.py::main" },
      { id: "utils.py::parse_file", label: "utils.py::parse_file" },
      { id: "utils.py::process_data", label: "utils.py::process_data" },
      { id: "api.js::fetchData", label: "api.js::fetchData" },
      { id: "api.js::processResponse", label: "api.js::processResponse" },
      { id: "model.java::calculate", label: "model.java::calculate" }
    ],
    links: [
      { source: "main.py::main", target: "utils.py::parse_file" },
      { source: "main.py::main", target: "utils.py::process_data" },
      { source: "utils.py::parse_file", target: "api.js::fetchData" },
      { source: "api.js::fetchData", target: "api.js::processResponse" },
      { source: "utils.py::process_data", target: "model.java::calculate" }
    ]
  };
}

function initializeGraphInIframe(doc, graphData) {
  // This function will be called after the iframe loads
  // It passes the graph data to the iframe context to initialize the visualization
  const iframe = doc.defaultView || doc.parentWindow;
  if (iframe && iframe.initializeGraphWithData) {
    iframe.initializeGraphWithData(graphData);
  }
}

function createGraphHTML() {
  // This returns the HTML content for the iframe, based on the graph.html file
  // but modified to accept data from the parent page
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Function Call Graph</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #f8f9fa;
        }
        #container {
            position: relative;
            width: 100vw;
            height: 100vh;
        }
        svg {
            width: 100%;
            height: 100%;
            cursor: grab;
        }
        svg:active {
            cursor: grabbing;
        }
        .node {
            stroke: #fff;
            stroke-width: 1.5px;
        }
        .link {
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 1px;
            marker-end: url(#arrow);
        }
        .node text {
            font-size: 10px;
            fill: #333;
            pointer-events: none;
        }
        .controls {
            position: absolute;
            top: 20px;
            left: 20px;
            background-color: rgba(255, 255, 255, 0.8);
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            z-index: 10;
        }
        .search-box {
            margin-bottom: 10px;
        }
        input {
            padding: 5px;
            width: 200px;
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        button {
            padding: 5px 10px;
            margin: 0 5px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .tooltip {
            position: absolute;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            z-index: 20;
        }
        #loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 18px;
            color: #666;
        }
    </style>
</head>
<body>
    <div id="container">
        <div id="loading">Loading visualization...</div>
        <div class="tooltip"></div>
        <div class="controls">
            <div class="search-box">
                <input type="text" id="search" placeholder="Search for a function...">
                <button id="search-btn">Find</button>
            </div>
            <div>
                <button id="zoom-in">Zoom In</button>
                <button id="zoom-out">Zoom Out</button>
                <button id="reset">Reset View</button>
            </div>
            <div style="margin-top: 10px;">
                <button id="toggle-labels">Toggle Labels</button>
                <button id="export-svg">Export SVG</button>
            </div>
            <div style="margin-top: 10px;">
                <span>Nodes: <span id="node-count">0</span>, Edges: <span id="edge-count">0</span></span>
            </div>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <script>
        // Global variables
        let container, svg, g, zoom;
        let nodes = [];
        let links = [];
        let simulation;
        let showLabels = true;
        
        document.addEventListener('DOMContentLoaded', function() {
            // DOM elements
            container = document.getElementById('container');
            const searchInput = document.getElementById('search');
            const searchBtn = document.getElementById('search-btn');
            const zoomInBtn = document.getElementById('zoom-in');
            const zoomOutBtn = document.getElementById('zoom-out');
            const resetBtn = document.getElementById('reset');
            const toggleLabelsBtn = document.getElementById('toggle-labels');
            const exportSvgBtn = document.getElementById('export-svg');
            const loadingIndicator = document.getElementById('loading');
            const tooltip = document.querySelector('.tooltip');
            const nodeCountSpan = document.getElementById('node-count');
            const edgeCountSpan = document.getElementById('edge-count');
            
            setup();
            
            // Event listeners
            searchBtn.addEventListener('click', searchNode);
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') searchNode();
            });
            
            zoomInBtn.addEventListener('click', () => {
                svg.transition().duration(300).call(zoom.scaleBy, 1.3);
            });
            
            zoomOutBtn.addEventListener('click', () => {
                svg.transition().duration(300).call(zoom.scaleBy, 0.7);
            });
            
            resetBtn.addEventListener('click', centerGraph);
            
            toggleLabelsBtn.addEventListener('click', toggleLabels);
            
            exportSvgBtn.addEventListener('click', exportSVG);
            
            // Expose function to parent window
            window.initializeGraphWithData = function(graphData) {
                initializeGraph(graphData);
                loadingIndicator.style.display = 'none';
            };
        });
        
        function setup() {
            // SVG setup
            const width = container.offsetWidth;
            const height = container.offsetHeight;
            
            svg = d3.select(container).append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // Add arrow marker for edges
            svg.append('defs').append('marker')
                .attr('id', 'arrow')
                .attr('viewBox', '0 -5 10 10')
                .attr('refX', 20)
                .attr('refY', 0)
                .attr('markerWidth', 6)
                .attr('markerHeight', 6)
                .attr('orient', 'auto')
                .append('path')
                .attr('d', 'M0,-5L10,0L0,5')
                .attr('fill', '#999');
            
            // Create a group for the graph
            g = svg.append('g');
            
            // Setup zoom behavior
            zoom = d3.zoom()
                .scaleExtent([0.1, 8])
                .on('zoom', (event) => {
                    g.attr('transform', event.transform);
                });
            
            svg.call(zoom);
        }
        
        // Initialize the visualization
        function initializeGraph(graphData) {
            const width = container.offsetWidth;
            const height = container.offsetHeight;
            
            // Update counters
            document.getElementById('node-count').textContent = graphData.nodes.length;
            document.getElementById('edge-count').textContent = graphData.links.length;
            
            nodes = graphData.nodes;
            links = graphData.links;
            
            // Limit nodes and links if too many
            if (nodes.length > 500) {
                console.warn('Graph is very large (\${nodes.length} nodes). Limiting to 500 nodes.');
                // Find nodes with connections first
                const nodeUsageCounts = new Map();
                links.forEach(link => {
                    nodeUsageCounts.set(link.source, (nodeUsageCounts.get(link.source) || 0) + 1);
                    nodeUsageCounts.set(link.target, (nodeUsageCounts.get(link.target) || 0) + 1);
                });
                
                // Sort nodes by usage count
                const sortedNodes = [...nodes].sort((a, b) => {
                    const countA = nodeUsageCounts.get(a.id) || 0;
                    const countB = nodeUsageCounts.get(b.id) || 0;
                    return countB - countA;
                });
                
                nodes = sortedNodes.slice(0, 500);
                const keepNodeIds = new Set(nodes.map(n => n.id));
                
                // Filter links to only include the kept nodes
                links = links.filter(link => 
                    keepNodeIds.has(typeof link.source === 'object' ? link.source.id : link.source) && 
                    keepNodeIds.has(typeof link.target === 'object' ? link.target.id : link.target)
                );
            }
            
            if (links.length > 1000) {
                console.warn('Too many edges (\${links.length}). Limiting to 1000 edges.');
                links = links.slice(0, 1000);
            }
            
            // Create force simulation
            simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('x', d3.forceX(width / 2).strength(0.1))
                .force('y', d3.forceY(height / 2).strength(0.1));
            
            // Draw links
            const link = g.append('g')
                .attr('class', 'links')
                .selectAll('line')
                .data(links)
                .enter()
                .append('line')
                .attr('class', 'link');
            
            // Draw nodes
            const node = g.append('g')
                .attr('class', 'nodes')
                .selectAll('g')
                .data(nodes)
                .enter()
                .append('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            node.append('circle')
                .attr('r', 5)
                .attr('fill', d => getNodeColor(d))
                .on('mouseover', showTooltip)
                .on('mouseout', hideTooltip)
                .on('click', highlightConnections);
            
            // Add labels
            const labels = node.append('text')
                .attr('dx', 8)
                .attr('dy', '.35em')
                .text(d => {
                    // Shorten the label if it's too long
                    const label = d.label;
                    if (label.length > 25) {
                        return label.substring(0, 22) + '...';
                    }
                    return label;
                })
                .style('display', showLabels ? 'block' : 'none');
            
            // Update simulation on tick
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node
                    .attr('transform', d => \`translate(\${d.x},\${d.y})\`);
            });
            
            // Center the graph
            centerGraph();
            
            // Function to derive node color
            function getNodeColor(d) {
                // Color based on outgoing connections
                const outgoingCount = links.filter(l => 
                    (typeof l.source === 'object' ? l.source.id : l.source) === d.id
                ).length;
                
                if (outgoingCount > 10) return '#e41a1c'; // Red for highly connected
                if (outgoingCount > 5) return '#ff7f00';  // Orange for medium connected
                if (outgoingCount > 0) return '#4daf4a';  // Green for some connections
                return '#377eb8';  // Blue for leaf nodes
            }
            
            // Show tooltip on hover
            function showTooltip(event, d) {
                const outCount = links.filter(l => 
                    (typeof l.source === 'object' ? l.source.id : l.source) === d.id
                ).length;
                
                const inCount = links.filter(l => 
                    (typeof l.target === 'object' ? l.target.id : l.target) === d.id
                ).length;
                
                tooltip.style.opacity = 1;
                tooltip.innerHTML = \`
                    <div><strong>\${d.label}</strong></div>
                    <div>Calls: \${outCount} functions</div>
                    <div>Called by: \${inCount} functions</div>
                \`;
                
                tooltip.style.left = (event.pageX + 10) + 'px';
                tooltip.style.top = (event.pageY + 10) + 'px';
            }
            
            function hideTooltip() {
                tooltip.style.opacity = 0;
            }
            
            // Highlight connections on click
            function highlightConnections(event, d) {
                // Reset previous highlights
                link.style('stroke', '#999').style('stroke-width', '1px');
                node.select('circle').style('stroke', '#fff').style('stroke-width', '1.5px');
                
                // Highlight this node
                d3.select(this).style('stroke', '#ff0000').style('stroke-width', '3px');
                
                // Highlight direct connections
                const connected = new Set();
                connected.add(d.id);
                
                // Find incoming connections
                link.filter(l => (typeof l.target === 'object' ? l.target.id : l.target) === d.id)
                    .style('stroke', '#ff0000')
                    .style('stroke-width', '2px')
                    .each(function(l) {
                        connected.add(typeof l.source === 'object' ? l.source.id : l.source);
                    });
                
                // Find outgoing connections
                link.filter(l => (typeof l.source === 'object' ? l.source.id : l.source) === d.id)
                    .style('stroke', '#0000ff')
                    .style('stroke-width', '2px')
                    .each(function(l) {
                        connected.add(typeof l.target === 'object' ? l.target.id : l.target);
                    });
                
                // Highlight connected nodes
                node.filter(n => connected.has(n.id) && n.id !== d.id)
                    .select('circle')
                    .style('stroke', '#ff7f00')
                    .style('stroke-width', '3px');
                
                // Show tooltip with more details
                showTooltip(event, d);
            }
            
            // Drag functions
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
        }
        
        // Center the graph in view
        function centerGraph() {
            const width = container.offsetWidth;
            const height = container.offsetHeight;
            
            const initialTransform = d3.zoomIdentity
                .translate(width / 2, height / 2)
                .scale(0.5);
            
            svg.call(zoom.transform, initialTransform);
        }
        
        // Search for a node
        function searchNode() {
            const searchTerm = document.getElementById('search').value.toLowerCase();
            if (!searchTerm) return;
            
            // Find matching nodes
            const matchingNodes = nodes.filter(n => 
                n.label.toLowerCase().includes(searchTerm)
            );
            
            if (matchingNodes.length > 0) {
                // Focus on the first matching node
                const node = matchingNodes[0];
                
                // Calculate transform to center on this node
                const scale = 1.2;
                const width = container.offsetWidth;
                const height = container.offsetHeight;
                const x = width / 2 - node.x * scale;
                const y = height / 2 - node.y * scale;
                
                const transform = d3.zoomIdentity
                    .translate(x, y)
                    .scale(scale);
                
                // Apply the transform with transition
                svg.transition()
                    .duration(750)
                    .call(zoom.transform, transform);
                
                // Highlight the found node
                d3.selectAll('.node circle')
                    .style('stroke', '#fff')
                    .style('stroke-width', '1.5px');
                
                d3.selectAll('.node')
                    .filter(d => d.id === node.id)
                    .select('circle')
                    .style('stroke', '#ff0000')
                    .style('stroke-width', '3px');
            } else {
                alert('No matching nodes found');
            }
        }
        
        // Toggle node labels
        function toggleLabels() {
            showLabels = !showLabels;
            d3.selectAll('.node text')
                .style('display', showLabels ? 'block' : 'none');
        }
        
        // Export SVG function
        function exportSVG() {
            // Create a copy of the SVG
            const svgCopy = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svgCopy.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
            
            const width = container.offsetWidth;
            const height = container.offsetHeight;
            svgCopy.setAttribute('width', width);
            svgCopy.setAttribute('height', height);
            
            // Copy the SVG content
            const svgContent = svg.node().cloneNode(true);
            svgCopy.appendChild(svgContent);
            
            // Create a downloadable blob
            const svgBlob = new Blob([svgCopy.outerHTML], {type: 'image/svg+xml'});
            const url = URL.createObjectURL(svgBlob);
            
            // Create download link
            const link = document.createElement('a');
            link.href = url;
            link.download = 'function_call_graph.svg';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    </script>
</body>
</html>`;
}

if (isGitHubRepoPage()) {
  createCodeLensButton();
}
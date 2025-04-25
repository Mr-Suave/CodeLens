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

// Reusable outside click handler for overlays
function handleOutsideClick(e, container, button) {
  const rect = container.getBoundingClientRect();
  if (
    e.clientX < rect.left ||
    e.clientX > rect.right ||
    e.clientY < rect.top ||
    e.clientY > rect.bottom
  ) {
    container.remove();
    // Do not show the button again
    document.removeEventListener('click', handleOutsideClick);
  }
}

// Reusable outside click handler for graph container
function handleGraphOutsideClick(e, container, button) {
  const rect = container.getBoundingClientRect();
  const iframe = container.querySelector('iframe');
  if (iframe && iframe.contains(e.target)) {
    return;
  }
  if (
    e.clientX < rect.left ||
    e.clientX > rect.right ||
    e.clientY < rect.top ||
    e.clientY > rect.bottom
  ) {
    e.preventDefault();
    e.stopPropagation();
    container.remove();
    // Do not show the button or reopen the overlay
    document.removeEventListener('click', handleGraphOutsideClick);
  }
}

// Reusable outside click handler for the CodeLens button
function handleButtonOutsideClick(e, button) {
  const rect = button.getBoundingClientRect();
  const overlay = document.getElementById('codelens-overlay');
  const graphContainer = document.getElementById('codelens-graph-container');
  // Only proceed if neither overlay nor graph is present
  if (!overlay && !graphContainer) {
    if (
      e.clientX < rect.left ||
      e.clientX > rect.right ||
      e.clientY < rect.top ||
      e.clientY > rect.bottom
    ) {
      button.remove();
      document.removeEventListener('click', handleButtonOutsideClick);
    }
  }
}

function createCodeLensButton() {
  const button = document.createElement('div');
  button.id = 'codelens-btn';
  button.innerText = 'CodeLens';
  document.body.appendChild(button);

  button.onclick = () => {
    const overlay = document.createElement('div');
    overlay.id = 'codelens-overlay';
    // Hide the CodeLens button permanently
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
    docBtn.addEventListener('click', showAudienceSelection); // Added event listener

    // Second Button: Commit Messages Graph
    const graphBtn = document.createElement('button');
    graphBtn.className = 'overlay-btn';
    graphBtn.innerText = 'View Commit Messages Graph';
    
    // Add event listener for the graph button
    graphBtn.addEventListener('click', showFunctionCallGraph);

    overlay.appendChild(docBtn);
    overlay.appendChild(graphBtn);

    // Third Button: Commit History Graph (with overlay image)
    const historyBtn = document.createElement('button');
    historyBtn.className = 'overlay-btn';
    historyBtn.innerText = 'View Commit History Graph';
    historyBtn.addEventListener('click', () => {
      const imageOverlay = document.createElement('div');
      imageOverlay.id = 'image-overlay';
      imageOverlay.style.position = 'fixed';
      imageOverlay.style.top = '0';
      imageOverlay.style.left = '0';
      imageOverlay.style.width = '100vw';
      imageOverlay.style.height = '100vh';
      imageOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
      imageOverlay.style.display = 'flex';
      imageOverlay.style.justifyContent = 'center';
      imageOverlay.style.alignItems = 'center';
      imageOverlay.style.zIndex = '10000';

      const img = document.createElement('img');
      img.src = chrome.runtime.getURL('images/commit_history.png'); // Correct image path
      img.alt = 'Commit History Graph';
      img.style.maxWidth = '90%';
      img.style.maxHeight = '90%';
      img.style.border = '4px solid white';
      img.style.borderRadius = '12px';
      imageOverlay.appendChild(img);

      const closeBtn = document.createElement('button');
      closeBtn.innerText = '×';
      closeBtn.style.position = 'absolute';
      closeBtn.style.top = '20px';
      closeBtn.style.right = '30px';
      closeBtn.style.fontSize = '36px';
      closeBtn.style.color = 'white';
      closeBtn.style.background = 'transparent';
      closeBtn.style.border = 'none';
      closeBtn.style.cursor = 'pointer';
      closeBtn.addEventListener('click', () => {
        imageOverlay.remove();
      });

      imageOverlay.appendChild(closeBtn);
      document.body.appendChild(imageOverlay);
    });
    overlay.appendChild(historyBtn);

    document.body.appendChild(overlay);

    // Add outside click handler for overlay
    setTimeout(() => {
      document.addEventListener('click', (e) => handleOutsideClick(e, overlay, button));
    }, 100);
  };

  // Add outside click handler for button
  setTimeout(() => {
    document.addEventListener('click', (e) => handleButtonOutsideClick(e, button));
  }, 100);
}


const USER_DOCUMENTATION_FILES = {
  "Novice developer": "Documentation_novice.md",
  "Client": "Documentation_client.md",
  "Senior developer": "Documentation_senior.md"
};

function showAudienceSelection() {
  const oldOverlay = document.getElementById('codelens-overlay');
  if (oldOverlay) {
    oldOverlay.remove();
  }
  
  const audienceOverlay = document.createElement('div');
  audienceOverlay.id = 'codelens-overlay';
  
  const title = document.createElement('h2');
  title.className = 'codelens-title';
  title.innerText = 'CodeLens';
  audienceOverlay.appendChild(title);
  
  const audienceHeading = document.createElement('h3');
  audienceHeading.className = 'codelens-subtitle';
  audienceHeading.innerText = 'Whom do you want to generate the document for?';
  audienceOverlay.appendChild(audienceHeading);
  
  const btnContainer = document.createElement('div');
  btnContainer.className = 'button-container';
  btnContainer.style.display = 'flex';
  btnContainer.style.gap = '10px';
  
  const audiences = ['Novice developer', 'Client', 'Senior developer'];
  let selectedAudience = null;
  
  audiences.forEach(audience => {
    const audienceBtn = document.createElement('button');
    audienceBtn.className = 'overlay-btn';
    audienceBtn.innerText = audience;
    audienceBtn.style.fontSize = '16px';
    
    audienceBtn.addEventListener('click', () => {
      document.querySelectorAll('.overlay-btn').forEach(btn => {
        btn.classList.remove('active-btn');
      });
      
      audienceBtn.classList.add('active-btn');
      selectedAudience = audience;
      
      if (!document.getElementById('find-doc-btn')) {
        const findDocBtn = document.createElement('button');
        findDocBtn.id = 'find-doc-btn';
        findDocBtn.className = 'overlay-btn find-btn';
        findDocBtn.innerText = 'Find Documentation';
        
        findDocBtn.addEventListener('click', () => {
          findDocumentationForAudience(selectedAudience);
        });
        
        audienceOverlay.appendChild(findDocBtn);
      }
    });
    
    btnContainer.appendChild(audienceBtn);
  });
  
  audienceOverlay.appendChild(btnContainer);
  document.body.appendChild(audienceOverlay);
  
  const backButton = document.createElement('button');
  backButton.className = 'back-btn';
  backButton.innerText = '← Back';
  backButton.addEventListener('click', () => {
    audienceOverlay.remove();
    // Do not show the CodeLens button
  });
  audienceOverlay.appendChild(backButton);
  
  // Add outside click handler
  setTimeout(() => {
    document.addEventListener('click', (e) => handleOutsideClick(e, audienceOverlay, document.getElementById('codelens-btn')));
  }, 100);
}

async function findDocumentationForAudience(audience) {
  const repoInfo = getRepoInfo();
  if (!repoInfo) {
    showError('Could not determine repository information.');
    return;
  }

  const fileName = USER_DOCUMENTATION_FILES[audience];
  const overlay = document.getElementById('codelens-overlay');
  if (!overlay) return;

  const loadingMsg = document.createElement('div');
  loadingMsg.className = 'loading-message';
  loadingMsg.innerText = `Searching for ${fileName}...`;
  overlay.appendChild(loadingMsg);

  try {
    const defaultBranch = await fetchDefaultBranch(repoInfo.owner, repoInfo.repo);
    const fileInfo = await searchDirectoryForFile(repoInfo.owner, repoInfo.repo, defaultBranch, "", fileName);
    
    if (!fileInfo) {
      throw new Error(`Documentation file ${fileName} not found in the repository.`);
    }

    const content = await fetchFileContent(fileInfo.download_url);
    loadingMsg.remove();

    const docContent = document.createElement('div');
    docContent.className = 'doc-content';
    docContent.style.padding = '20px';
    docContent.style.backgroundColor = 'rgba(0, 0, 0, 0.85)';
    docContent.style.border = '2px solid #e0e0e0';
    docContent.style.borderRadius = '10px';
    docContent.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    docContent.style.maxHeight = '70vh';
    docContent.style.overflow = 'auto';
    docContent.style.fontFamily = "'Georgia', serif";

    const pathInfo = document.createElement('p');
    pathInfo.innerText = `Source: ${content.path}`;
    pathInfo.style.fontWeight = 'bold';
    pathInfo.style.color = '#ffffff';
    pathInfo.style.margin = '0 0 15px 0';
    docContent.appendChild(pathInfo);

    const formattedContent = document.createElement('div');
    formattedContent.className = 'markdown-content';
    formattedContent.style.lineHeight = '1.8';
    formattedContent.style.color = '#ffffff';

    const markdownText = content.content;
    const formattedHtml = markdownToHtml(markdownText);
    formattedContent.innerHTML = formattedHtml;

    docContent.appendChild(formattedContent);
    overlay.appendChild(docContent);
  } catch (error) {
    loadingMsg.remove();
    showError(error.message);
  }
}

function markdownToHtml(markdown) {
  let html = markdown
    .replace(/^# (.+)$/gm, '<h1 style="color:#ffffff;font-size:28px;border-bottom:3px solid #3498db;padding-bottom:10px;margin:20px 0;">$1</h1>')
    .replace(/^## (.+)$/gm, '<h2 style="color:#ffffff;font-size:24px;border-bottom:2px solid #27ae60;padding-bottom:8px;margin:18px 0;">$1</h2>')
    .replace(/^### (.+)$/gm, '<h3 style="color:#ffffff;font-size:20px;border-bottom:1px solid #c0392b;padding-bottom:6px;margin:15px 0;">$1</h3>')
    .replace(/^#### (.+)$/gm, '<h4 style="color:#ffffff;font-size:18px;margin:15px 0;">$1</h4>')
    
    .replace(/\*\*([^*]+)\*\*/g, '<strong style="color:#ffffff;">$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em style="color:#ffffff;">$1</em>')
    
    .replace(/```([^`]+)```/g, '<pre style="background-color:#f9f9f9;padding:15px;border-left:4px solid #3498db;border-radius:5px;overflow:auto;"><code style="color:#2c3e50;">$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code style="background-color:#ecf0f1;padding:2px 6px;border-radius:3px;color:#7f8c8d;">$1</code>')
    
    .replace(/^- (.+)$/gm, '<li style="color:#ffffff;margin-bottom:10px;">$1</li>')
    
    .replace(/\n\n/g, '<br><br>');

  html = html.replace(/<li[^>]*>(.+?)(?=<li|$)/gs, function(match) {
    return '<ul style="margin:15px 0 15px 25px;list-style-type:square;">' + match + '</ul>';
  });

  return html;
}

async function fetchDefaultBranch(owner, repo) {
  const response = await fetch(`https://api.github.com/repos/${owner}/${repo}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch repository info: ${response.status}`);
  }
  const data = await response.json();
  return data.default_branch || 'main';
}

async function searchDirectoryForFile(owner, repo, branch, path, fileName) {
  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${path}?ref=${branch}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch directory contents: ${response.status}`);
  }
  const items = await response.json();

  const foundFile = items.find(item => 
    item.type === 'file' && item.name.toLowerCase() === fileName.toLowerCase()
  );
  if (foundFile) {
    return foundFile;
  }

  const subDirPromises = items
    .filter(item => item.type === 'dir')
    .map(dir => {
      const newPath = path ? `${path}/${dir.name}` : dir.name;
      return searchDirectoryForFile(owner, repo, branch, newPath, fileName);
    });

  const results = await Promise.all(subDirPromises);
  return results.find(result => result !== null) || null;
}

async function fetchFileContent(downloadUrl) {
  const response = await fetch(downloadUrl);
  if (!response.ok) {
    throw new Error(`Failed to fetch file content: ${response.status}`);
  }
  const content = await response.text();
  return {
    content,
    path: downloadUrl.split('/').slice(-2).join('/')
  };
}

function showError(message) {
  const overlay = document.getElementById('codelens-overlay');
  if (overlay) {
    const errorMsg = document.createElement('div');
    errorMsg.className = 'error-message';
    errorMsg.style.color = 'red';
    errorMsg.style.padding = '10px';
    errorMsg.innerText = `Error: ${message}`;
    overlay.appendChild(errorMsg);
  }
}

function showFunctionCallGraph() {
  const repoInfo = getRepoInfo();
  if (!repoInfo) {
    alert('Could not determine repository information.');
    return;
  }

  const codeLensButton = document.getElementById('codelens-btn');

  let graphContainer = document.getElementById('codelens-graph-container');
  if (graphContainer) {
    graphContainer.remove();
  }

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
    // Do not show the CodeLens button
    document.removeEventListener('click', handleGraphOutsideClick);
  };
  graphContainer.appendChild(closeButton);
  
  const backButton = document.createElement('div');
  backButton.style.position = 'absolute';
  backButton.style.top = '20px';
  backButton.style.left = '20px';
  backButton.style.color = 'white';
  backButton.style.backgroundColor = '#555';
  backButton.style.padding = '8px 12px';
  backButton.style.borderRadius = '4px';
  backButton.style.cursor = 'pointer';
  backButton.style.fontSize = '14px';
  backButton.style.fontWeight = 'bold';
  backButton.innerText = '← Back';
  backButton.onclick = () => {
    graphContainer.remove();
    // Do not show the CodeLens button or reopen the overlay
    document.removeEventListener('click', handleGraphOutsideClick);
  };
  graphContainer.appendChild(backButton);

  const loadingIndicator = document.createElement('div');
  loadingIndicator.style.color = 'white';
  loadingIndicator.style.textAlign = 'center';
  loadingIndicator.style.marginTop = '50px';
  loadingIndicator.innerText = 'Searching for function_list.txt in repository...';
  graphContainer.appendChild(loadingIndicator);

  // Add outside click handler with delay
  setTimeout(() => {
    document.addEventListener('click', (e) => handleGraphOutsideClick(e, graphContainer, codeLensButton));
  }, 100);

  fetchFunctionList(repoInfo)
    .then(functionListContent => {
      renderFunctionCallGraph(graphContainer, functionListContent);
    })
    .catch(error => {
      console.error('Error fetching function list:', error);
      graphContainer.innerHTML = '';
      graphContainer.appendChild(closeButton);
      graphContainer.appendChild(backButton);
      
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
  const url = `https://raw.githubusercontent.com/${repoInfo.owner}/${repoInfo.repo}/dil/main/function_list.txt`;
  
  try {
    const response = await fetch(url);
    if (response.ok) {
      return await response.text();
    }
    
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
  container.innerHTML = '';
  
  const graphFrame = document.createElement('iframe');
  graphFrame.id = 'function-graph-frame';
  graphFrame.style.width = '100%';
  graphFrame.style.height = '100%';
  graphFrame.style.border = 'none';
  container.appendChild(graphFrame);
  
  graphFrame.onload = () => {
    const doc = graphFrame.contentDocument || graphFrame.contentWindow.document;
    
    if (functionListContent) {
      const graphData = parseAndPrepareFunctionList(functionListContent);
      initializeGraphInIframe(doc, graphData);
    } else {
      const sampleData = createSampleGraphData();
      initializeGraphInIframe(doc, sampleData);
    }
  };
  
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
  const iframe = doc.defaultView || doc.parentWindow;
  if (iframe && iframe.initializeGraphWithData) {
    iframe.initializeGraphWithData(graphData);
  }
}

function createGraphHTML() {
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
        let container, svg, g, zoom;
        let nodes = [];
        let links = [];
        let simulation;
        let showLabels = true;
        
        document.addEventListener('DOMContentLoaded', function() {
            try {
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
                
                searchBtn.addEventListener('click', searchNode);
                searchInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') searchNode();
                });
                
                zoomInBtn.addEventListener('click', function() {
                    svg.transition().duration(300).call(zoom.scaleBy, 1.3);
                });
                
                zoomOutBtn.addEventListener('click', function() {
                    svg.transition().duration(300).call(zoom.scaleBy, 0.7);
                });
                
                resetBtn.addEventListener('click', centerGraph);
                
                toggleLabelsBtn.addEventListener('click', toggleLabels);
                
                exportSvgBtn.addEventListener('click', exportSVG);
                
                window.initializeGraphWithData = function(graphData) {
                    initializeGraph(graphData);
                    loadingIndicator.style.display = 'none';
                };
            } catch (error) {
                console.error('Error initializing graph:', error);
            }
        });
        
        function setup() {
            const width = container.offsetWidth;
            const height = container.offsetHeight;
            
            svg = d3.select(container).append('svg')
                .attr('width', width)
                .attr('height', height);
            
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
            
            g = svg.append('g');
            
            zoom = d3.zoom()
                .scaleExtent([0.1, 8])
                .on('zoom', function(event) {
                    g.attr('transform', event.transform);
                });
            
            svg.call(zoom);
        }
        
        function initializeGraph(graphData) {
            try {
                const width = container.offsetWidth;
                const height = container.offsetHeight;
                
                document.getElementById('node-count').textContent = graphData.nodes.length;
                document.getElementById('edge-count').textContent = graphData.links.length;
                
                nodes = graphData.nodes;
                links = graphData.links;
                
                if (nodes.length > 500) {
                    console.warn('Graph is very large (' + nodes.length + ' nodes). Limiting to 500 nodes.');
                    const nodeUsageCounts = new Map();
                    links.forEach(function(link) {
                        nodeUsageCounts.set(link.source, (nodeUsageCounts.get(link.source) || 0) + 1);
                        nodeUsageCounts.set(link.target, (nodeUsageCounts.get(link.target) || 0) + 1);
                    });
                    
                    const sortedNodes = nodes.slice().sort(function(a, b) {
                        const countA = nodeUsageCounts.get(a.id) || 0;
                        const countB = nodeUsageCounts.get(b.id) || 0;
                        return countB - countA;
                    });
                    
                    nodes = sortedNodes.slice(0, 500);
                    const keepNodeIds = new Set(nodes.map(function(n) { return n.id; }));
                    
                    links = links.filter(function(link) {
                        return keepNodeIds.has(typeof link.source === 'object' ? link.source.id : link.source) &&
                               keepNodeIds.has(typeof link.target === 'object' ? link.target.id : link.target);
                    });
                }
                
                if (links.length > 1000) {
                    console.warn('Too many edges (' + links.length + '). Limiting to 1000 edges.');
                    links = links.slice(0, 1000);
                }
                
                simulation = d3.forceSimulation(nodes)
                    .force('link', d3.forceLink(links).id(function(d) { return d.id; }).distance(100))
                    .force('charge', d3.forceManyBody().strength(-300))
                    .force('center', d3.forceCenter(width / 2, height / 2))
                    .force('x', d3.forceX(width / 2).strength(0.1))
                    .force('y', d3.forceY(height / 2).strength(0.1));
                
                const link = g.append('g')
                    .attr('class', 'links')
                    .selectAll('line')
                    .data(links)
                    .enter()
                    .append('line')
                    .attr('class', 'link');
                
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
                    .attr('fill', getNodeColor)
                    .on('mouseover', showTooltip)
                    .on('mouseout', hideTooltip)
                    .on('click', highlightConnections);
                
                const labels = node.append('text')
                    .attr('dx', 8)
                    .attr('dy', '.35em')
                    .text(function(d) {
                        const label = d.label;
                        if (label.length > 25) {
                            return label.substring(0, 22) + '...';
                        }
                        return label;
                    })
                    .style('display', showLabels ? 'block' : 'none');
                
                simulation.on('tick', function() {
                    link
                        .attr('x1', function(d) { return d.source.x; })
                        .attr('y1', function(d) { return d.source.y; })
                        .attr('x2', function(d) { return d.target.x; })
                        .attr('y2', function(d) { return d.target.y; });
                    
                    node
                        .attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; });
                });
                
                centerGraph();
                
                function getNodeColor(d) {
                    const outgoingCount = links.filter(function(l) {
                        return (typeof l.source === 'object' ? l.source.id : l.source) === d.id;
                    }).length;
                    
                    if (outgoingCount > 10) return '#e41a1c';
                    if (outgoingCount > 5) return '#ff7f00';
                    if (outgoingCount > 0) return '#4daf4a';
                    return '#377eb8';
                }
                
                function showTooltip(event, d) {
                    const outCount = links.filter(function(l) {
                        return (typeof l.source === 'object' ? l.source.id : l.source) === d.id;
                    }).length;
                    
                    const inCount = links.filter(function(l) {
                        return (typeof l.target === 'object' ? l.target.id : l.target) === d.id;
                    }).length;
                    
                    tooltip.style.opacity = 1;
                    tooltip.innerHTML = '<div><strong>' + d.label + '</strong></div>' +
                                       '<div>Calls: ' + outCount + ' functions</div>' +
                                       '<div>Called by: ' + inCount + ' functions</div>';
                    
                    tooltip.style.left = (event.pageX + 10) + 'px';
                    tooltip.style.top = (event.pageY + 10) + 'px';
                }
                
                function hideTooltip() {
                    tooltip.style.opacity = 0;
                }
                
                function highlightConnections(event, d) {
                    link.style('stroke', '#999').style('stroke-width', '1px');
                    node.select('circle').style('stroke', '#fff').style('stroke-width', '1.5px');
                    
                    d3.select(this).style('stroke', '#ff0000').style('stroke-width', '3px');
                    
                    const connected = new Set();
                    connected.add(d.id);
                    
                    link.filter(function(l) { return (typeof l.target === 'object' ? l.target.id : l.target) === d.id; })
                        .style('stroke', '#ff0000')
                        .style('stroke-width', '2px')
                        .each(function(l) {
                            connected.add(typeof l.source === 'object' ? l.source.id : l.source);
                        });
                    
                    link.filter(function(l) { return (typeof l.source === 'object' ? l.source.id : l.source) === d.id; })
                        .style('stroke', '#0000ff')
                        .style('stroke-width', '2px')
                        .each(function(l) {
                            connected.add(typeof l.target === 'object' ? l.target.id : l.target);
                        });
                    
                    node.filter(function(n) { return connected.has(n.id) && n.id !== d.id; })
                        .select('circle')
                        .style('stroke', '#ff7f00')
                        .style('stroke-width', '3px');
                    
                    showTooltip(event, d);
                }
                
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
            } catch (error) {
                console.error('Error in initializeGraph:', error);
            }
        }
        
        function centerGraph() {
            const width = container.offsetWidth;
            const height = container.offsetHeight;
            
            const initialTransform = d3.zoomIdentity
                .translate(width / 2, height / 2)
                .scale(0.5);
            
            svg.call(zoom.transform, initialTransform);
        }
        
        function searchNode() {
            const searchTerm = document.getElementById('search').value.toLowerCase();
            if (!searchTerm) return;
            
            const matchingNodes = nodes.filter(function(n) {
                return n.label.toLowerCase().includes(searchTerm);
            });
            
            if (matchingNodes.length > 0) {
                const node = matchingNodes[0];
                
                const scale = 1.2;
                const width = container.offsetWidth;
                const height = container.offsetHeight;
                const x = width / 2 - node.x * scale;
                const y = height / 2 - node.y * scale;
                
                const transform = d3.zoomIdentity
                    .translate(x, y)
                    .scale(scale);
                
                svg.transition()
                    .duration(750)
                    .call(zoom.transform, transform);
                
                d3.selectAll('.node circle')
                    .style('stroke', '#fff')
                    .style('stroke-width', '1.5px');
                
                d3.selectAll('.node')
                    .filter(function(d) { return d.id === node.id; })
                    .select('circle')
                    .style('stroke', '#ff0000')
                    .style('stroke-width', '3px');
            } else {
                alert('No matching nodes found');
            }
        }
        
        function toggleLabels() {
            showLabels = !showLabels;
            d3.selectAll('.node text')
                .style('display', showLabels ? 'block' : 'none');
        }
        
        function exportSVG() {
            const svgCopy = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svgCopy.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
            const width = container.offsetWidth;
            const height = container.offsetHeight;
            svgCopy.setAttribute('width', width);
            svgCopy.setAttribute('height', height);
            
            const svgContent = svg.node().cloneNode(true);
            svgCopy.appendChild(svgContent);
            
            const svgBlob = new Blob([svgCopy.outerHTML], {type: 'image/svg+xml'});
            const url = URL.createObjectURL(svgBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = 'function_call_graph.svg';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>`;
}

if (isGitHubRepoPage()) {
  createCodeLensButton();
}
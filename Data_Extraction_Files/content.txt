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

function handleOutsideClick(e, container, button) {
  const rect = container.getBoundingClientRect();
  if (
    e.clientX < rect.left ||
    e.clientX > rect.right ||
    e.clientY < rect.top ||
    e.clientY > rect.bottom
  ) {
    container.remove();
    document.removeEventListener('click', handleOutsideClick);
  }
}

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
    document.removeEventListener('click', handleGraphOutsideClick);
  }
}

function handleButtonOutsideClick(e, button) {
  const rect = button.getBoundingClientRect();
  const overlay = document.getElementById('codelens-overlay');
  const graphContainer = document.getElementById('codelens-graph-container');
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
    button.style.display = 'none';

    const title = document.createElement('h2');
    title.className = 'codelens-title';
    title.innerText = 'CodeLens';
    overlay.appendChild(title);

    const subtitle = document.createElement('h3');
    subtitle.className = 'codelens-subtitle';
    subtitle.innerText = 'Documentation making just got easier!';
    overlay.appendChild(subtitle);

    const docBtn = document.createElement('button');
    docBtn.className = 'overlay-btn';
    docBtn.innerText = 'View Documentation For the Repository';
    docBtn.addEventListener('click', showAudienceSelection);

    const graphBtn = document.createElement('button');
    graphBtn.className = 'overlay-btn';
    graphBtn.innerText = 'View Function Call Graph';
    graphBtn.addEventListener('click', showFunctionCallGraph);

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
    overlay.appendChild(docBtn);
    overlay.appendChild(graphBtn);
    overlay.appendChild(historyBtn);

    document.body.appendChild(overlay);

    setTimeout(() => {
      document.addEventListener('click', (e) => handleOutsideClick(e, overlay, button));
    }, 100);
  };

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
  });
  audienceOverlay.appendChild(backButton);
  
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

  const overlayRect = overlay.getBoundingClientRect();
  const originalPosition = {
    top: overlayRect.top,
    right: window.innerWidth - overlayRect.right,
    width: overlayRect.width
  };

  overlay.innerHTML = '';

  const loadingMsg = document.createElement('div');
  loadingMsg.className = 'loading-message';
  loadingMsg.innerText = `Searching for ${fileName}...`;
  loadingMsg.style.padding = '20px';
  loadingMsg.style.textAlign = 'center';
  overlay.appendChild(loadingMsg);

  try {
    const defaultBranch = await fetchDefaultBranch(repoInfo.owner, repoInfo.repo);
    const fileInfo = await searchDirectoryForFile(repoInfo.owner, repoInfo.repo, defaultBranch, "", fileName);
    
    if (!fileInfo) {
      throw new Error(`Documentation file ${fileName} not found in the repository.`);
    }

    const content = await fetchFileContent(fileInfo.download_url);
    loadingMsg.remove();

    overlay.style.position = 'fixed';
    overlay.style.top = `${originalPosition.top}px`;
    overlay.style.right = `${originalPosition.right}px`;
    overlay.style.width = `${originalPosition.width}px`;
    overlay.style.height = '90vh';
    overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
    overlay.style.zIndex = '9999';
    overlay.style.borderRadius = '10px';
    overlay.style.boxShadow = '0 0 20px rgba(0, 0, 0, 0.4)';
    overlay.style.display = 'flex';
    overlay.style.flexDirection = 'column';
    overlay.style.padding = '15px';
    overlay.style.boxSizing = 'border-box';

    const header = document.createElement('div');
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'center';
    header.style.marginBottom = '15px';
    
    const docTitle = document.createElement('h2');
    docTitle.innerText = `Documentation for ${audience}`;
    docTitle.style.color = '#ffffff';
    docTitle.style.margin = '0';
    header.appendChild(docTitle);
    
    const backButton = document.createElement('button');
    backButton.className = 'back-btn';
    backButton.innerText = '← Back';
    backButton.style.cursor = 'pointer';
    backButton.style.padding = '5px 10px';
    backButton.style.backgroundColor = '#444';
    backButton.style.color = '#fff';
    backButton.style.border = 'none';
    backButton.style.borderRadius = '4px';
    backButton.style.position = 'absolute';
    backButton.style.top = '0';
    backButton.style.left = '0';
    backButton.addEventListener('click', showAudienceSelection);
    header.appendChild(backButton);
    
    overlay.appendChild(header);

    const docContent = document.createElement('div');
    docContent.style.flex = '1';
    docContent.style.overflow = 'auto';
    docContent.style.backgroundColor = 'rgba(20, 20, 20, 0.8)';
    docContent.style.borderRadius = '8px';
    docContent.style.padding = '20px';
    docContent.style.fontFamily = "'Georgia', serif";
    docContent.style.color = '#ffffff';

    const pathInfo = document.createElement('p');
    pathInfo.innerText = `Source: ${content.path}`;
    pathInfo.style.fontWeight = 'bold';
    pathInfo.style.color = '#aaaaaa';
    pathInfo.style.marginBottom = '15px';
    pathInfo.style.borderBottom = '1px solid #444';
    pathInfo.style.paddingBottom = '10px';
    docContent.appendChild(pathInfo);

    const formattedContent = document.createElement('div');
    formattedContent.className = 'markdown-content';
    formattedContent.style.lineHeight = '1.8';

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
  console.log('showFunctionCallGraph: Starting');
  const repoInfo = getRepoInfo();
  if (!repoInfo) {
    console.error('showFunctionCallGraph: Could not determine repository information.');
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
    document.removeEventListener('click', handleGraphOutsideClick);
  };
  graphContainer.appendChild(backButton);

  const loadingIndicator = document.createElement('div');
  loadingIndicator.style.color = 'white';
  loadingIndicator.style.textAlign = 'center';
  loadingIndicator.style.marginTop = '50px';
  loadingIndicator.innerText = 'Searching for function_list.txt in repository...';
  graphContainer.appendChild(loadingIndicator);

  setTimeout(() => {
    document.addEventListener('click', (e) => handleGraphOutsideClick(e, graphContainer, codeLensButton));
  }, 100);

  console.log('showFunctionCallGraph: Fetching function list');
  fetchFunctionList(repoInfo)
    .then(functionListContent => {
      console.log('showFunctionCallGraph: Function list fetched successfully');
      loadingIndicator.remove();
      renderFunctionCallGraph(graphContainer, functionListContent);
    })
    .catch(error => {
      console.error('showFunctionCallGraph: Error fetching function list:', error);
      loadingIndicator.remove();
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
        <p>Using sample data instead.</p>
      `;
      graphContainer.appendChild(errorMessage);
      
      console.log('showFunctionCallGraph: Falling back to sample data');
      renderFunctionCallGraph(graphContainer, null);
    });
}

async function fetchFunctionList(repoInfo) {
  console.log('fetchFunctionList: Attempting to fetch function_list.txt');
  try {
    const defaultBranch = await fetchDefaultBranch(repoInfo.owner, repoInfo.repo);
    const fileInfo = await searchDirectoryForFile(repoInfo.owner, repoInfo.repo, defaultBranch, "", "function_list.txt");
    if (!fileInfo) {
      throw new Error('function_list.txt not found in repository');
    }
    const response = await fetch(fileInfo.download_url);
    if (!response.ok) {
      throw new Error(`Failed to fetch function_list.txt: ${response.status}`);
    }
    console.log('fetchFunctionList: Successfully fetched function_list.txt');
    return await response.text();
  } catch (error) {
    console.error('fetchFunctionList: Error:', error);
    throw error;
  }
}

function renderFunctionCallGraph(container, functionListContent) {
  console.log('renderFunctionCallGraph: Starting with functionListContent:', !!functionListContent);
  container.innerHTML = '';
  
  const graphFrame = document.createElement('iframe');
  graphFrame.id = 'function-graph-frame';
  graphFrame.style.width = '100%';
  graphFrame.style.height = '100%';
  graphFrame.style.border = 'none';
  graphFrame.style.backgroundColor = '#f8f9fa';
  container.appendChild(graphFrame);
  
  graphFrame.onload = () => {
    console.log('renderFunctionCallGraph: Iframe onload triggered');
    try {
      // Parse and send graph data to iframe
      let graphData;
      if (functionListContent) {
        console.log('renderFunctionCallGraph: Parsing function list content');
        graphData = parseAndPrepareFunctionList(functionListContent);
        console.log('renderFunctionCallGraph: Graph data:', graphData);
      } else {
        console.log('renderFunctionCallGraph: Using sample data');
        graphData = createSampleGraphData();
        console.log('renderFunctionCallGraph: Sample data:', graphData);
      }
      
      // Send graph data to iframe via postMessage
      graphFrame.contentWindow.postMessage({
        type: 'renderGraph',
        graphData
      }, '*');
    } catch (error) {
      console.error('renderFunctionCallGraph: Error preparing graph data:', error);
      container.innerHTML = '<div style="color: red; padding: 20px;">Error: Failed to prepare graph data.</div>';
    }
  };
  
  const graphHTML = createGraphHTML();
  const blob = new Blob([graphHTML], { type: 'text/html' });
  const blobUrl = URL.createObjectURL(blob);
  console.log('renderFunctionCallGraph: Setting iframe src to:', blobUrl);
  graphFrame.src = blobUrl;
}

function parseAndPrepareFunctionList(content) {
  console.log('parseAndPrepareFunctionList: Starting');
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
  
  const result = {
    nodes: Array.from(nodes.values()),
    links
  };
  console.log('parseAndPrepareFunctionList: Result:', result);
  return result;
}

function createSampleGraphData() {
  console.log('createSampleGraphData: Generating sample data');
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

function createGraphHTML() {
  console.log('createGraphHTML: Generating HTML');
  const d3Src = chrome.runtime.getURL('lib/d3.min.js');
  const graphSrc = chrome.runtime.getURL('graph.js');
  console.log('createGraphHTML: Script sources:', { d3Src, graphSrc });
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
            width: 100%;
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
        #error {
            color: red;
            padding: 20px;
            text-align: center;
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
    <script src="${d3Src}"></script>
    <script src="${graphSrc}"></script>
</body>
</html>`;
}

if (isGitHubRepoPage()) {
  createCodeLensButton();
}
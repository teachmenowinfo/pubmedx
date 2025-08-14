// Global variables
let currentGraphId = null;
let statusPollingInterval = null;
let graphData = null;
let simulation = null;

// DOM elements
const pmidForm = document.getElementById('pmidForm');
const pmidInput = document.getElementById('pmidInput');
const loadingSection = document.getElementById('loadingSection');
const graphSection = document.getElementById('graphSection');
const errorSection = document.getElementById('errorSection');
const loadingStatus = document.getElementById('loadingStatus');
const progressFill = document.getElementById('progressFill');
const errorMessage = document.getElementById('errorMessage');
const graphVisualization = document.getElementById('graphVisualization');
const articleDetails = document.getElementById('articleDetails');
const detailsContent = document.getElementById('detailsContent');
const closeDetails = document.getElementById('closeDetails');
const resetView = document.getElementById('resetView');
const exportGraph = document.getElementById('exportGraph');

// Event listeners
pmidForm.addEventListener('submit', handleFormSubmit);
closeDetails.addEventListener('click', hideArticleDetails);
resetView.addEventListener('click', resetGraphView);
exportGraph.addEventListener('click', exportGraphData);

// Form submission handler
async function handleFormSubmit(event) {
  event.preventDefault();
  
  const pmid = pmidInput.value.trim();
  
  if (!pmid) {
    showError('Please enter a valid PMID');
    return;
  }
  
  // Show loading state
  showLoading();
  hideError();
  
  try {
    // Create graph
    const response = await fetch('/api/graph/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        pmid: pmid,
        max_depth: 1  // Always use depth 1 for direct connections only
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    currentGraphId = result.graph_id;
    
    // Start polling for status
    startStatusPolling();
    
  } catch (error) {
    console.error('Error creating graph:', error);
    showError('Failed to create graph. Please try again.');
    hideLoading();
  }
}

// Status polling
function startStatusPolling() {
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval);
  }
  
  statusPollingInterval = setInterval(async () => {
    try {
      const response = await fetch(`/api/graph/${currentGraphId}/status`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const status = await response.json();
      updateLoadingStatus(status);
      
      if (status.status === 'completed' || status.status === 'completed_with_limit') {
        clearInterval(statusPollingInterval);
        await loadGraphData();
      } else if (status.status === 'error') {
        clearInterval(statusPollingInterval);
        showError('Graph generation failed. Please try again.');
        hideLoading();
      }
      
    } catch (error) {
      console.error('Error polling status:', error);
      clearInterval(statusPollingInterval);
      showError('Failed to check graph status. Please try again.');
      hideLoading();
    }
  }, 2000); // Poll every 2 seconds
}

// Update loading status
function updateLoadingStatus(status) {
  const total = status.total_articles || 1;
  const processed = status.processed_articles || 0;
  const percentage = Math.min((processed / total) * 100, 100);
  
  let statusText = `Processed ${processed} articles...`;
  
  if (status.limit_reached) {
    statusText += ' (Reached maximum article limit)';
  }
  
  loadingStatus.textContent = statusText;
  progressFill.style.width = `${percentage}%`;
}

// Load graph data
async function loadGraphData() {
  try {
    const response = await fetch(`/api/graph/${currentGraphId}/data`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    graphData = await response.json();
    hideLoading();
    showGraph();
    renderGraph();
    
    // Show limit warning if applicable
    if (graphData.metadata.limit_reached) {
      showLimitWarning();
    }
    
  } catch (error) {
    console.error('Error loading graph data:', error);
    showError('Failed to load graph data. Please try again.');
    hideLoading();
  }
}

// Show limit warning
function showLimitWarning() {
  const warningDiv = document.createElement('div');
  warningDiv.className = 'limit-warning';
  warningDiv.innerHTML = `
    <div class="warning-content">
      <strong>Note:</strong> Graph generation was limited to 50 articles to respect API rate limits. 
      This shows the most important direct references and citations of your article.
    </div>
  `;
  
  const graphHeader = document.querySelector('.graph-header');
  graphHeader.appendChild(warningDiv);
}

// Render D3.js graph
function renderGraph() {
  if (!graphData || !graphData.nodes || !graphData.edges) {
    return;
  }
  
  // Clear previous graph
  d3.select(graphVisualization).selectAll("*").remove();
  
  const width = graphVisualization.clientWidth;
  const height = graphVisualization.clientHeight;
  
  // Create SVG
  const svg = d3.select(graphVisualization)
    .append("svg")
    .attr("width", width)
    .attr("height", height);
  
  // Create tooltip
  const tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);
  
  // Create force simulation
  simulation = d3.forceSimulation(graphData.nodes)
    .force("link", d3.forceLink(graphData.edges).id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(30));
  
  // Create links
  const link = svg.append("g")
    .selectAll("line")
    .data(graphData.edges)
    .enter().append("line")
    .attr("class", d => `link ${d.type}`)
    .attr("marker-end", "url(#arrow)");
  
  // Create arrow marker
  svg.append("defs").append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15)
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", "#999");
  
  // Create nodes
  const node = svg.append("g")
    .selectAll("circle")
    .data(graphData.nodes)
    .enter().append("circle")
    .attr("class", d => `node ${d.is_seed ? 'seed' : ''}`)
    .attr("r", d => d.is_seed ? 8 : 6)
    .attr("fill", d => d.is_seed ? "#ff6b6b" : "#667eea")
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended))
    .on("click", showArticleDetails)
    .on("mouseover", function(event, d) {
      tooltip.transition()
        .duration(200)
        .style("opacity", .9);
      tooltip.html(`
        <strong>${d.title}</strong><br/>
        PMID: ${d.id}<br/>
        ${d.authors ? d.authors.slice(0, 3).join(', ') + (d.authors.length > 3 ? '...' : '') : ''}
      `)
        .style("left", (event.pageX + 5) + "px")
        .style("top", (event.pageY - 28) + "px");
    })
    .on("mouseout", function(d) {
      tooltip.transition()
        .duration(500)
        .style("opacity", 0);
    });
  
  // Add node labels
  const label = svg.append("g")
    .selectAll("text")
    .data(graphData.nodes)
    .enter().append("text")
    .attr("class", "node-label")
    .text(d => d.id)
    .attr("dy", 20);
  
  // Update positions on simulation tick
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
    
    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
    
    label
      .attr("x", d => d.x)
      .attr("y", d => d.y);
  });
  
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

// Show article details
function showArticleDetails(event, d) {
  const node = graphData.nodes.find(n => n.id === d.id);
  if (!node) return;
  
  detailsContent.innerHTML = `
    <div class="article-title">${node.title}</div>
    <div class="article-meta">
      <p><strong>PMID:</strong> ${node.id}</p>
      ${node.authors ? `<p><strong>Authors:</strong> ${node.authors.join(', ')}</p>` : ''}
      ${node.journal ? `<p><strong>Journal:</strong> ${node.journal}</p>` : ''}
      ${node.pubdate ? `<p><strong>Published:</strong> ${node.pubdate}</p>` : ''}
    </div>
    ${node.abstract ? `<div class="article-abstract"><strong>Abstract:</strong><br/>${node.abstract}</div>` : ''}
  `;
  
  articleDetails.classList.remove('hidden');
}

// Hide article details
function hideArticleDetails() {
  articleDetails.classList.add('hidden');
}

// Reset graph view
function resetGraphView() {
  if (simulation) {
    simulation.alpha(1).restart();
  }
}

// Export graph data
function exportGraphData() {
  if (!graphData) return;
  
  const dataStr = JSON.stringify(graphData, null, 2);
  const dataBlob = new Blob([dataStr], {type: 'application/json'});
  const url = URL.createObjectURL(dataBlob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `pubmed-graph-${currentGraphId}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Show/hide functions
function showLoading() {
  loadingSection.classList.remove('hidden');
  graphSection.classList.add('hidden');
  errorSection.classList.add('hidden');
}

function hideLoading() {
  loadingSection.classList.add('hidden');
}

function showGraph() {
  graphSection.classList.remove('hidden');
}

function showError(message) {
  errorMessage.textContent = message;
  errorSection.classList.remove('hidden');
}

function hideError() {
  errorSection.classList.add('hidden');
}

// Handle window resize
window.addEventListener('resize', () => {
  if (graphData) {
    renderGraph();
  }
}); 
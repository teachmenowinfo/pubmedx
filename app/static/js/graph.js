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
const analyticsBtn = document.getElementById('analyticsBtn');
const analyticsSection = document.getElementById('analyticsSection');
const closeAnalyticsBtn = document.getElementById('closeAnalyticsBtn');
const analyticsLoading = document.getElementById('analyticsLoading');
const analyticsData = document.getElementById('analyticsData');

// Event listeners
pmidForm.addEventListener('submit', handleFormSubmit);
closeDetails.addEventListener('click', hideArticleDetails);
resetView.addEventListener('click', resetGraphView);
exportGraph.addEventListener('click', exportGraphData);
analyticsBtn.addEventListener('click', showAnalytics);
closeAnalyticsBtn.addEventListener('click', hideAnalytics);

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

// Analytics functions
async function showAnalytics() {
  if (!currentGraphId) return;
  
  analyticsSection.classList.remove('hidden');
  analyticsLoading.style.display = 'block';
  analyticsData.style.display = 'none';
  
  try {
    const response = await fetch(`/api/graph/${currentGraphId}/analytics`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    displayAnalytics(result.analytics);
    
  } catch (error) {
    console.error('Error fetching analytics:', error);
    analyticsData.innerHTML = '<div class="error">Failed to load analytics. Please try again.</div>';
    analyticsData.style.display = 'block';
  } finally {
    analyticsLoading.style.display = 'none';
  }
}

function hideAnalytics() {
  analyticsSection.classList.add('hidden');
}

function displayAnalytics(analytics) {
  if (analytics.error) {
    analyticsData.innerHTML = `<div class="error">${analytics.error}</div>`;
    analyticsData.style.display = 'block';
    return;
  }
  
  let html = '';
  
  // Summary card
  if (analytics.summary) {
    html += createAnalyticsCard('Summary', analytics.summary);
  }
  
  // Basic statistics
  if (analytics.basic_statistics) {
    html += createAnalyticsCard('Basic Statistics', analytics.basic_statistics);
  }
  
  // Centrality measures
  if (analytics.centrality_measures) {
    html += createCentralityCard(analytics.centrality_measures);
  }
  
  // Clustering analysis
  if (analytics.clustering_analysis) {
    html += createClusteringCard(analytics.clustering_analysis);
  }
  
  // Research insights
  if (analytics.research_insights) {
    html += createInsightsCard(analytics.research_insights);
  }
  
  analyticsData.innerHTML = html;
  analyticsData.style.display = 'block';
}

function createAnalyticsCard(title, data) {
  let html = `<div class="analytics-card">
    <h3>${title}</h3>`;
  
  for (const [key, value] of Object.entries(data)) {
    if (typeof value === 'object' && value !== null) continue;
    
    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    const formattedValue = typeof value === 'number' ? value.toFixed(3) : value;
    
    html += `<div class="analytics-metric">
      <span class="metric-label">${formattedKey}</span>
      <span class="metric-value">${formattedValue}</span>
    </div>`;
  }
  
  html += '</div>';
  return html;
}

function createCentralityCard(centralityData) {
  let html = `<div class="analytics-card">
    <h3>Centrality Measures</h3>`;
  
  for (const [measure, scores] of Object.entries(centralityData)) {
    if (typeof scores !== 'object' || !scores) continue;
    
    const topNodes = Object.entries(scores)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5);
    
    if (topNodes.length > 0) {
      const measureName = measure.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      html += `<h4>${measureName}</h4><ul class="insights-list">`;
      
      topNodes.forEach(([nodeId, score]) => {
        html += `<li>
          <span>PMID: ${nodeId}</span>
          <span class="insight-score">${score.toFixed(4)}</span>
        </li>`;
      });
      
      html += '</ul>';
    }
  }
  
  html += '</div>';
  return html;
}

function createClusteringCard(clusteringData) {
  let html = `<div class="analytics-card">
    <h3>Clustering Analysis</h3>`;
  
  if (clusteringData.global_clustering !== undefined) {
    html += `<div class="analytics-metric">
      <span class="metric-label">Global Clustering Coefficient</span>
      <span class="metric-value">${clusteringData.global_clustering.toFixed(4)}</span>
    </div>`;
  }
  
  if (clusteringData.number_of_communities !== undefined) {
    html += `<div class="analytics-card">
      <h4>Research Communities</h4>
      <div class="analytics-metric">
        <span class="metric-label">Number of Communities</span>
        <span class="metric-value">${clusteringData.number_of_communities}</span>
      </div>`;
    
    if (clusteringData.community_sizes) {
      const topCommunities = Object.entries(clusteringData.community_sizes)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3);
      
      html += '<ul class="insights-list">';
      topCommunities.forEach(([communityId, size]) => {
        html += `<li>
          <span>Community ${communityId}</span>
          <span class="insight-score">${size} articles</span>
        </li>`;
      });
      html += '</ul>';
    }
    
    html += '</div>';
  }
  
  html += '</div>';
  return html;
}

function createInsightsCard(insightsData) {
  let html = `<div class="analytics-card">
    <h3>Research Insights</h3>`;
  
  if (insightsData.top_influential_papers) {
    html += `<h4>Top Influential Papers</h4><ul class="insights-list">`;
    insightsData.top_influential_papers.forEach(([pmid, score]) => {
      html += `<li>
        <span>PMID: ${pmid}</span>
        <span class="insight-score">${score.toFixed(4)}</span>
      </li>`;
    });
    html += '</ul>';
  }
  
  if (insightsData.bridge_papers) {
    html += `<h4>Bridge Papers</h4><ul class="insights-list">`;
    insightsData.bridge_papers.forEach(([pmid, score]) => {
      html += `<li>
        <span>PMID: ${pmid}</span>
        <span class="insight-score">${score.toFixed(4)}</span>
      </li>`;
    });
    html += '</ul>';
  }
  
  if (insightsData.emerging_topics) {
    html += `<h4>Emerging Topics</h4><ul class="insights-list">`;
    insightsData.emerging_topics.forEach(([pmid, outDegree, inDegree]) => {
      html += `<li>
        <span>PMID: ${pmid}</span>
        <span class="insight-score">${outDegree}→ ${inDegree}←</span>
      </li>`;
    });
    html += '</ul>';
  }
  
  html += '</div>';
  return html;
} 
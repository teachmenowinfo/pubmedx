# PubMed Knowledge Graph

An interactive web application that generates knowledge graphs from PubMed articles, showing citation relationships and references up to three layers deep.

## Features

- **Interactive Graph Visualization**: Beautiful D3.js-powered force-directed graphs
- **Multi-layer Crawling**: Explore references and citations up to 3 layers deep
- **Real-time Progress Tracking**: Monitor graph building progress with live updates
- **Article Details**: Click on nodes to view detailed article information
- **Export Functionality**: Download graph data as JSON
- **Responsive Design**: Works on desktop and mobile devices
- **Rate Limiting**: Respects PubMed API limits with intelligent delays

## Screenshots

The application provides:
- Clean, modern interface with gradient background
- PMID input form with depth selection
- Real-time loading progress with spinner
- Interactive graph visualization with drag-and-drop
- Article details sidebar
- Export and reset controls

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd pubmedx
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Open your browser** and navigate to `http://localhost:8000`

## Usage

### Web Interface

1. **Enter a PMID**: Input a valid PubMed ID (e.g., `32284615`)
2. **Select Depth**: Choose how many layers to crawl (1-3)
3. **Generate Graph**: Click the button to start building
4. **Monitor Progress**: Watch the real-time progress indicator
5. **Explore**: Once complete, interact with the graph:
   - Drag nodes to reposition
   - Click nodes to view article details
   - Use controls to reset view or export data

### API Endpoints

The application also provides REST API endpoints:

- `POST /api/graph/create` - Create a new graph
- `GET /api/graph/{graph_id}/status` - Check graph status
- `GET /api/graph/{graph_id}/data` - Get graph data
- `GET /api/graph/list` - List all graphs
- `DELETE /api/graph/{graph_id}` - Delete a graph

### Example API Usage

```bash
# Create a graph
curl -X POST "http://localhost:8000/api/graph/create" \
  -H "Content-Type: application/json" \
  -d '{"pmid": "32284615", "max_depth": 2}'

# Check status
curl "http://localhost:8000/api/graph/{graph_id}/status"

# Get graph data
curl "http://localhost:8000/api/graph/{graph_id}/data"
```

## Architecture

### Backend Components

- **FastAPI**: Modern web framework for API endpoints
- **PubMed Service**: Handles NCBI E-utilities API calls with rate limiting
- **Graph Service**: Manages graph construction using NetworkX
- **Background Tasks**: Asynchronous graph building

### Frontend Components

- **D3.js**: Interactive graph visualization
- **Vanilla JavaScript**: Form handling and API communication
- **CSS3**: Modern styling with gradients and animations
- **HTML5**: Semantic markup with responsive design

### Data Flow

1. User submits PMID → API creates graph
2. Background task crawls PubMed API → Builds relationships
3. Real-time status updates → Frontend polling
4. Graph completion → D3.js visualization
5. User interaction → Article details display

## Technical Details

### PubMed API Integration

- Uses NCBI E-utilities API
- Implements rate limiting (3 requests/second)
- Handles references and citations
- Graceful error handling for missing data

### Graph Construction

- **NetworkX**: Graph data structure
- **Breadth-first traversal**: Level-by-level crawling
- **Deduplication**: Prevents cycles and duplicates
- **Depth limiting**: Configurable exploration depth

### Performance Considerations

- **Async processing**: Non-blocking API calls
- **Background tasks**: Long-running operations
- **Caching**: In-memory graph storage
- **Rate limiting**: Respects API quotas

## Testing

Run the test script to verify functionality:

```bash
python3 test_pubmed_graph.py
```

This will:
- Test PubMed API connectivity
- Verify graph construction
- Demonstrate the complete workflow

## Configuration

### Environment Variables

- `PUBMED_API_DELAY`: Rate limiting delay (default: 0.34s)
- `MAX_GRAPH_DEPTH`: Maximum crawl depth (default: 3)
- `PORT`: Server port (default: 8000)

### Rate Limiting

The application respects PubMed API limits:
- 3 requests per second maximum
- Automatic retry with exponential backoff
- Graceful degradation for rate limit errors

## Limitations

- **API Rate Limits**: PubMed API has strict rate limits
- **Data Availability**: Not all articles have complete reference data
- **Memory Usage**: Large graphs can consume significant memory
- **Processing Time**: Deep graphs may take several minutes to build

## Future Enhancements

- **Persistent Storage**: Database integration for graph persistence
- **Advanced Filtering**: Filter by date, journal, author, etc.
- **Graph Analytics**: Centrality, clustering, path analysis
- **Batch Processing**: Multiple PMIDs simultaneously
- **Export Formats**: CSV, GraphML, GEXF support
- **User Accounts**: Save and share graphs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **NCBI**: For providing the PubMed API
- **D3.js**: For the excellent graph visualization library
- **FastAPI**: For the modern Python web framework
- **NetworkX**: For graph data structures and algorithms 
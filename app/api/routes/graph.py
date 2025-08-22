from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
import asyncio
from app.services.graph_service import GraphService

router = APIRouter(prefix="/api/graph", tags=["graph"])

# Global graph service instance
graph_service = GraphService()

class CreateGraphRequest(BaseModel):
    pmid: str
    max_depth: Optional[int] = 3

class GraphResponse(BaseModel):
    graph_id: str
    status: str
    message: str

class AnalyticsResponse(BaseModel):
    graph_id: str
    analytics: dict

@router.post("/create", response_model=GraphResponse)
async def create_graph(request: CreateGraphRequest, background_tasks: BackgroundTasks):
    """Create a new knowledge graph from a seed PMID"""
    try:
        # Generate unique graph ID
        graph_id = str(uuid.uuid4())
        
        # Create the graph
        graph_info = graph_service.create_graph(graph_id, request.pmid)
        
        # Start building the graph in the background
        background_tasks.add_task(
            graph_service.build_graph, 
            graph_id, 
            request.max_depth
        )
        
        return GraphResponse(
            graph_id=graph_id,
            status="initializing",
            message=f"Graph creation started for PMID {request.pmid}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{graph_id}/status")
async def get_graph_status(graph_id: str):
    """Get the current status of a graph"""
    status = graph_service.get_graph_status(graph_id)
    if not status:
        raise HTTPException(status_code=404, detail="Graph not found")
    return status

@router.get("/{graph_id}/data")
async def get_graph_data(graph_id: str):
    """Get the complete graph data for visualization"""
    data = graph_service.get_graph_data(graph_id)
    if not data:
        raise HTTPException(status_code=404, detail="Graph not found")
    return data

@router.get("/list")
async def list_graphs():
    """List all graphs"""
    return graph_service.list_graphs()

@router.delete("/{graph_id}")
async def delete_graph(graph_id: str):
    """Delete a graph"""
    if graph_id in graph_service.graphs:
        del graph_service.graphs[graph_id]
        return {"message": f"Graph {graph_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Graph not found")

@router.get("/{graph_id}/analytics")
async def get_graph_analytics(graph_id: str):
    """Get comprehensive analytics for a graph"""
    analytics = graph_service.get_graph_analytics(graph_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Graph not found or not completed")
    return AnalyticsResponse(graph_id=graph_id, analytics=analytics)

@router.get("/{graph_id}/nodes/{node_id}/analytics")
async def get_node_analytics(graph_id: str, node_id: str):
    """Get detailed analytics for a specific node in a graph"""
    analytics = graph_service.get_node_analytics(graph_id, node_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Node or graph not found")
    return {
        "graph_id": graph_id,
        "node_id": node_id,
        "analytics": analytics
    } 
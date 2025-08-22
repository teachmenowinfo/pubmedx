import networkx as nx
import asyncio
import json
from typing import Dict, List, Set, Optional
from datetime import datetime
import logging
from .pubmed_service import PubMedService
from .analytics_service import GraphAnalyticsService

logger = logging.getLogger(__name__)

class GraphService:
    """Service for building and managing PubMed knowledge graphs"""
    
    def __init__(self):
        self.pubmed_service = PubMedService()
        self.analytics_service = GraphAnalyticsService()
        self.graphs = {}  # Store multiple graphs by ID
        self.MAX_ARTICLES = 50  # Limit to prevent overwhelming the API
        
    def create_graph(self, graph_id: str, seed_pmid: str) -> Dict:
        """Create a new knowledge graph"""
        graph = nx.DiGraph()
        graph.graph['id'] = graph_id
        graph.graph['seed_pmid'] = seed_pmid
        graph.graph['created_at'] = datetime.now().isoformat()
        graph.graph['status'] = 'initializing'
        graph.graph['total_articles'] = 0
        graph.graph['processed_articles'] = 0
        
        self.graphs[graph_id] = graph
        return {
            'graph_id': graph_id,
            'seed_pmid': seed_pmid,
            'status': 'initializing'
        }
    
    async def build_graph(self, graph_id: str, max_depth: int = 3) -> Dict:
        """Build the knowledge graph - only direct references and citations of seed article"""
        if graph_id not in self.graphs:
            raise ValueError(f"Graph {graph_id} not found")
        
        graph = self.graphs[graph_id]
        seed_pmid = graph.graph['seed_pmid']
        
        print(f"\n🚀 Starting graph construction for PMID {seed_pmid}")
        print("=" * 60)
        
        # Initialize tracking sets
        processed_pmids = set()
        to_process = [(seed_pmid, 0)]  # (pmid, depth)
        
        graph.graph['status'] = 'building'
        
        while to_process and len(processed_pmids) < self.MAX_ARTICLES:
            current_pmid, current_depth = to_process.pop(0)
            
            if current_pmid in processed_pmids:
                continue
                
            processed_pmids.add(current_pmid)
            graph.graph['processed_articles'] += 1
            
            print(f"\n📊 Processing article {len(processed_pmids)}/{self.MAX_ARTICLES}")
            
            try:
                # Get article details and relationships
                article_details, relationships = await asyncio.gather(
                    self.pubmed_service.get_article_details(current_pmid),
                    self.pubmed_service.get_article_relationships(current_pmid)
                )
                
                # Add node to graph
                if article_details:
                    graph.add_node(current_pmid, **article_details)
                else:
                    # Add placeholder node if details not available
                    graph.add_node(current_pmid, pmid=current_pmid, title=f"PMID: {current_pmid}")
                
                # Only add direct connections for the seed article (Layer 1)
                if current_pmid == seed_pmid:
                    print(f"🔗 Adding direct connections for seed article...")
                    
                    # Add edges for references (this article cites others)
                    for ref_pmid in relationships['references']:
                        if len(processed_pmids) < self.MAX_ARTICLES:
                            graph.add_edge(current_pmid, ref_pmid, relationship_type='cites')
                            if ref_pmid not in processed_pmids:
                                to_process.append((ref_pmid, 1))
                    
                    # Add edges for citations (other articles cite this one)
                    for citation_pmid in relationships['citations']:
                        if len(processed_pmids) < self.MAX_ARTICLES:
                            graph.add_edge(citation_pmid, current_pmid, relationship_type='cited_by')
                            if citation_pmid not in processed_pmids:
                                to_process.append((citation_pmid, 1))
                
                # Update total count
                graph.graph['total_articles'] = len(graph.nodes())
                
                # Small delay to be respectful to the API
                await asyncio.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Error processing PMID {current_pmid}: {e}")
                print(f"❌ Error processing PMID {current_pmid}: {e}")
                continue
        
        # Check if we hit the limit
        if len(processed_pmids) >= self.MAX_ARTICLES:
            graph.graph['status'] = 'completed_with_limit'
            graph.graph['limit_reached'] = True
            print(f"\n⚠️  Reached maximum article limit ({self.MAX_ARTICLES})")
        else:
            graph.graph['status'] = 'completed'
            print(f"\n✅ Completed processing all available articles")
            
        graph.graph['completed_at'] = datetime.now().isoformat()
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📈 GRAPH CONSTRUCTION SUMMARY")
        print("=" * 60)
        print(f"🎯 Seed PMID: {seed_pmid}")
        print(f"📊 Total Articles: {graph.graph['total_articles']}")
        print(f"🔗 Total Relationships: {len(graph.edges())}")
        print(f"📖 References: {len([e for e in graph.edges(data=True) if e[2].get('relationship_type') == 'cites'])}")
        print(f"📚 Citations: {len([e for e in graph.edges(data=True) if e[2].get('relationship_type') == 'cited_by'])}")
        print(f"⏱️  Status: {graph.graph['status']}")
        print("=" * 60)
        
        return {
            'graph_id': graph_id,
            'status': graph.graph['status'],
            'total_articles': graph.graph['total_articles'],
            'total_relationships': len(graph.edges()),
            'limit_reached': graph.graph.get('limit_reached', False)
        }
    
    def get_graph_data(self, graph_id: str) -> Optional[Dict]:
        """Get graph data for visualization"""
        if graph_id not in self.graphs:
            return None
        
        graph = self.graphs[graph_id]
        
        # Convert to format suitable for frontend visualization
        nodes = []
        for pmid, data in graph.nodes(data=True):
            nodes.append({
                'id': pmid,
                'title': data.get('title', f'PMID: {pmid}'),
                'authors': data.get('authors', []),
                'journal': data.get('journal', ''),
                'pubdate': data.get('pubdate', ''),
                'is_seed': pmid == graph.graph['seed_pmid']
            })
        
        edges = []
        for source, target, data in graph.edges(data=True):
            edges.append({
                'source': source,
                'target': target,
                'type': data.get('relationship_type', 'unknown')
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'graph_id': graph_id,
                'seed_pmid': graph.graph['seed_pmid'],
                'status': graph.graph['status'],
                'total_articles': graph.graph['total_articles'],
                'total_relationships': len(edges),
                'created_at': graph.graph['created_at'],
                'completed_at': graph.graph.get('completed_at'),
                'limit_reached': graph.graph.get('limit_reached', False)
            }
        }
    
    def get_graph_status(self, graph_id: str) -> Optional[Dict]:
        """Get current status of a graph"""
        if graph_id not in self.graphs:
            return None
        
        graph = self.graphs[graph_id]
        return {
            'graph_id': graph_id,
            'status': graph.graph['status'],
            'total_articles': graph.graph['total_articles'],
            'processed_articles': graph.graph['processed_articles'],
            'created_at': graph.graph['created_at'],
            'completed_at': graph.graph.get('completed_at'),
            'limit_reached': graph.graph.get('limit_reached', False)
        }
    
    def list_graphs(self) -> List[Dict]:
        """List all graphs"""
        return [
            {
                'graph_id': graph_id,
                'seed_pmid': graph.graph['seed_pmid'],
                'status': graph.graph['status'],
                'total_articles': graph.graph['total_articles'],
                'created_at': graph.graph['created_at']
            }
            for graph_id, graph in self.graphs.items()
        ]
    
    def get_graph_analytics(self, graph_id: str) -> Optional[Dict]:
        """Get comprehensive analytics for a graph"""
        if graph_id not in self.graphs:
            return None
        
        graph = self.graphs[graph_id]
        
        # Only analyze completed graphs
        if graph.graph.get('status') not in ['completed', 'completed_with_limit']:
            return {'error': 'Graph analysis only available for completed graphs'}
        
        try:
            print(f"\n📊 Generating analytics for graph {graph_id}...")
            analytics = self.analytics_service.analyze_graph(graph)
            print(f"✅ Analytics generated successfully")
            return analytics
        except Exception as e:
            logger.error(f"Error generating analytics for graph {graph_id}: {e}")
            return {'error': str(e)}
    
    def get_node_analytics(self, graph_id: str, node_id: str) -> Optional[Dict]:
        """Get detailed analytics for a specific node in a graph"""
        if graph_id not in self.graphs:
            return None
        
        graph = self.graphs[graph_id]
        
        try:
            analytics = self.analytics_service.get_node_analytics(graph, node_id)
            return analytics
        except Exception as e:
            logger.error(f"Error getting node analytics for {node_id} in graph {graph_id}: {e}")
            return {'error': str(e)}
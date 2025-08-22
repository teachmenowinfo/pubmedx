import networkx as nx
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class GraphAnalyticsService:
    """Service for analyzing graph properties and metrics"""
    
    def __init__(self):
        pass
    
    def analyze_graph(self, graph: nx.DiGraph) -> Dict:
        """
        Perform comprehensive graph analysis
        
        Args:
            graph: NetworkX directed graph
            
        Returns:
            Dictionary containing all analysis results
        """
        try:
            # Basic graph statistics
            basic_stats = self._get_basic_statistics(graph)
            
            # Centrality measures
            centrality_measures = self._calculate_centrality_measures(graph)
            
            # Clustering and community analysis
            clustering_analysis = self._analyze_clustering(graph)
            
            # Path analysis
            path_analysis = self._analyze_paths(graph)
            
            # Network structure analysis
            structure_analysis = self._analyze_network_structure(graph)
            
            # Research insights
            research_insights = self._generate_research_insights(graph, centrality_measures)
            
            return {
                'basic_statistics': basic_stats,
                'centrality_measures': centrality_measures,
                'clustering_analysis': clustering_analysis,
                'path_analysis': path_analysis,
                'network_structure': structure_analysis,
                'research_insights': research_insights,
                'summary': self._generate_summary(graph, centrality_measures, clustering_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing graph: {e}")
            return {'error': str(e)}
    
    def _get_basic_statistics(self, graph: nx.DiGraph) -> Dict:
        """Calculate basic graph statistics"""
        try:
            return {
                'total_nodes': graph.number_of_nodes(),
                'total_edges': graph.number_of_edges(),
                'density': nx.density(graph),
                'average_degree': sum(dict(graph.degree()).values()) / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0,
                'max_degree': max(dict(graph.degree()).values()) if graph.number_of_nodes() > 0 else 0,
                'min_degree': min(dict(graph.degree()).values()) if graph.number_of_nodes() > 0 else 0,
                'is_connected': nx.is_weakly_connected(graph),
                'number_of_components': nx.number_weakly_connected_components(graph),
                'largest_component_size': len(max(nx.weakly_connected_components(graph), key=len)) if graph.number_of_nodes() > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error calculating basic statistics: {e}")
            return {}
    
    def _calculate_centrality_measures(self, graph: nx.DiGraph) -> Dict:
        """Calculate various centrality measures for nodes"""
        try:
            # Convert to undirected for some centrality measures
            undirected_graph = graph.to_undirected()
            
            centrality_measures = {}
            
            # Degree centrality
            centrality_measures['degree_centrality'] = nx.degree_centrality(graph)
            
            # Betweenness centrality (can be slow for large graphs)
            try:
                centrality_measures['betweenness_centrality'] = nx.betweenness_centrality(graph, k=min(100, graph.number_of_nodes()))
            except:
                centrality_measures['betweenness_centrality'] = {}
            
            # Closeness centrality
            try:
                centrality_measures['closeness_centrality'] = nx.closeness_centrality(graph)
            except:
                centrality_measures['closeness_centrality'] = {}
            
            # Eigenvector centrality
            try:
                centrality_measures['eigenvector_centrality'] = nx.eigenvector_centrality_numpy(undirected_graph, max_iter=1000)
            except:
                centrality_measures['eigenvector_centrality'] = {}
            
            # PageRank
            try:
                centrality_measures['pagerank'] = nx.pagerank(graph, alpha=0.85)
            except:
                centrality_measures['pagerank'] = {}
            
            # HITS (Hubs and Authorities)
            try:
                hubs, authorities = nx.hits(graph, max_iter=1000)
                centrality_measures['hubs'] = hubs
                centrality_measures['authorities'] = authorities
            except:
                centrality_measures['hubs'] = {}
                centrality_measures['authorities'] = {}
            
            return centrality_measures
            
        except Exception as e:
            logger.error(f"Error calculating centrality measures: {e}")
            return {}
    
    def _analyze_clustering(self, graph: nx.DiGraph) -> Dict:
        """Analyze clustering and community structure"""
        try:
            # Convert to undirected for clustering analysis
            undirected_graph = graph.to_undirected()
            
            clustering_analysis = {}
            
            # Global clustering coefficient
            clustering_analysis['global_clustering'] = nx.average_clustering(undirected_graph)
            
            # Local clustering coefficients
            clustering_analysis['local_clustering'] = nx.clustering(undirected_graph)
            
            # Average local clustering
            clustering_analysis['average_local_clustering'] = np.mean(list(clustering_analysis['local_clustering'].values())) if clustering_analysis['local_clustering'] else 0
            
            # Community detection using Louvain method
            try:
                from community import community_louvain
                communities = community_louvain.best_partition(undirected_graph)
                clustering_analysis['communities'] = communities
                clustering_analysis['number_of_communities'] = len(set(communities.values()))
                
                # Community sizes
                community_sizes = defaultdict(int)
                for node, community in communities.items():
                    community_sizes[community] += 1
                clustering_analysis['community_sizes'] = dict(community_sizes)
                
            except ImportError:
                clustering_analysis['communities'] = {}
                clustering_analysis['number_of_communities'] = 0
                clustering_analysis['community_sizes'] = {}
            
            return clustering_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing clustering: {e}")
            return {}
    
    def _analyze_paths(self, graph: nx.DiGraph) -> Dict:
        """Analyze path properties and distances"""
        try:
            path_analysis = {}
            
            # Check if graph is strongly connected
            if nx.is_strongly_connected(graph):
                # Average shortest path length
                try:
                    path_analysis['average_shortest_path'] = nx.average_shortest_path_length(graph)
                except:
                    path_analysis['average_shortest_path'] = None
                
                # Diameter
                try:
                    path_analysis['diameter'] = nx.diameter(graph)
                except:
                    path_analysis['diameter'] = None
            else:
                # For disconnected graphs, analyze largest component
                largest_cc = max(nx.strongly_connected_components(graph), key=len)
                if len(largest_cc) > 1:
                    subgraph = graph.subgraph(largest_cc)
                    try:
                        path_analysis['average_shortest_path'] = nx.average_shortest_path_length(subgraph)
                        path_analysis['diameter'] = nx.diameter(subgraph)
                    except:
                        path_analysis['average_shortest_path'] = None
                        path_analysis['diameter'] = None
                else:
                    path_analysis['average_shortest_path'] = None
                    path_analysis['diameter'] = None
            
            # Eccentricity (for largest component)
            try:
                largest_cc = max(nx.strongly_connected_components(graph), key=len)
                if len(largest_cc) > 1:
                    subgraph = graph.subgraph(largest_cc)
                    eccentricity = nx.eccentricity(subgraph)
                    path_analysis['eccentricity'] = eccentricity
                    path_analysis['radius'] = min(eccentricity.values())
                else:
                    path_analysis['eccentricity'] = {}
                    path_analysis['radius'] = None
            except:
                path_analysis['eccentricity'] = {}
                path_analysis['radius'] = None
            
            return path_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing paths: {e}")
            return {}
    
    def _analyze_network_structure(self, graph: nx.DiGraph) -> Dict:
        """Analyze network structure and properties"""
        try:
            structure_analysis = {}
            
            # Degree distribution
            degrees = [d for n, d in graph.degree()]
            structure_analysis['degree_distribution'] = {
                'mean': np.mean(degrees),
                'median': np.median(degrees),
                'std': np.std(degrees),
                'min': min(degrees) if degrees else 0,
                'max': max(degrees) if degrees else 0
            }
            
            # Assortativity (degree correlation)
            try:
                structure_analysis['assortativity'] = nx.degree_assortativity_coefficient(graph)
            except:
                structure_analysis['assortativity'] = None
            
            # Reciprocity (for directed graphs)
            try:
                structure_analysis['reciprocity'] = nx.reciprocity(graph)
            except:
                structure_analysis['reciprocity'] = None
            
            # Transitivity
            try:
                structure_analysis['transitivity'] = nx.transitivity(graph)
            except:
                structure_analysis['transitivity'] = None
            
            # Node types analysis
            in_degrees = dict(graph.in_degree())
            out_degrees = dict(graph.out_degree())
            
            # Identify hubs (high out-degree) and authorities (high in-degree)
            avg_out_degree = np.mean(list(out_degrees.values()))
            avg_in_degree = np.mean(list(in_degrees.values()))
            
            hubs = [node for node, degree in out_degrees.items() if degree > avg_out_degree * 1.5]
            authorities = [node for node, degree in in_degrees.items() if degree > avg_in_degree * 1.5]
            
            structure_analysis['node_types'] = {
                'hubs': hubs,
                'authorities': authorities,
                'avg_out_degree': avg_out_degree,
                'avg_in_degree': avg_in_degree
            }
            
            return structure_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing network structure: {e}")
            return {}
    
    def _generate_research_insights(self, graph: nx.DiGraph, centrality_measures: Dict) -> Dict:
        """Generate research insights and recommendations"""
        try:
            insights = {}
            
            # Top influential papers
            if 'pagerank' in centrality_measures and centrality_measures['pagerank']:
                top_papers = sorted(centrality_measures['pagerank'].items(), key=lambda x: x[1], reverse=True)[:5]
                insights['top_influential_papers'] = top_papers
            
            # Bridge papers (high betweenness)
            if 'betweenness_centrality' in centrality_measures and centrality_measures['betweenness_centrality']:
                bridge_papers = sorted(centrality_measures['betweenness_centrality'].items(), key=lambda x: x[1], reverse=True)[:5]
                insights['bridge_papers'] = bridge_papers
            
            # Emerging topics (high out-degree, low in-degree)
            in_degrees = dict(graph.in_degree())
            out_degrees = dict(graph.out_degree())
            
            emerging_topics = []
            for node in graph.nodes():
                if out_degrees.get(node, 0) > 2 and in_degrees.get(node, 0) <= 1:
                    emerging_topics.append((node, out_degrees.get(node, 0), in_degrees.get(node, 0)))
            
            emerging_topics.sort(key=lambda x: x[1], reverse=True)
            insights['emerging_topics'] = emerging_topics[:5]
            
            # Research gaps (isolated or poorly connected nodes)
            isolated_nodes = list(nx.isolates(graph))
            insights['isolated_nodes'] = isolated_nodes
            
            # Well-connected clusters
            if graph.number_of_nodes() > 0:
                components = list(nx.weakly_connected_components(graph))
                well_connected = [comp for comp in components if len(comp) >= 3]
                insights['well_connected_clusters'] = [list(comp) for comp in well_connected[:3]]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating research insights: {e}")
            return {}
    
    def _generate_summary(self, graph: nx.DiGraph, centrality_measures: Dict, clustering_analysis: Dict) -> Dict:
        """Generate a summary of key findings"""
        try:
            summary = {}
            
            # Key metrics summary
            summary['key_metrics'] = {
                'total_articles': graph.number_of_nodes(),
                'total_connections': graph.number_of_edges(),
                'network_density': nx.density(graph),
                'is_connected': nx.is_weakly_connected(graph)
            }
            
            # Top papers by different measures
            if 'pagerank' in centrality_measures and centrality_measures['pagerank']:
                top_pagerank = max(centrality_measures['pagerank'].items(), key=lambda x: x[1])
                summary['most_influential_paper'] = top_pagerank
            
            if 'betweenness_centrality' in centrality_measures and centrality_measures['betweenness_centrality']:
                top_betweenness = max(centrality_measures['betweenness_centrality'].items(), key=lambda x: x[1])
                summary['most_bridging_paper'] = top_betweenness
            
            # Clustering summary
            if 'global_clustering' in clustering_analysis:
                summary['clustering_coefficient'] = clustering_analysis['global_clustering']
            
            if 'number_of_communities' in clustering_analysis:
                summary['research_communities'] = clustering_analysis['number_of_communities']
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {}
    
    def get_node_analytics(self, graph: nx.DiGraph, node_id: str) -> Dict:
        """Get detailed analytics for a specific node"""
        try:
            if node_id not in graph.nodes():
                return {'error': 'Node not found in graph'}
            
            node_analytics = {
                'node_id': node_id,
                'degree': graph.degree(node_id),
                'in_degree': graph.in_degree(node_id),
                'out_degree': graph.out_degree(node_id),
                'neighbors': list(graph.neighbors(node_id)),
                'predecessors': list(graph.predecessors(node_id)),
                'successors': list(graph.successors(node_id))
            }
            
            # Add centrality measures if available
            centrality_measures = self._calculate_centrality_measures(graph)
            
            for measure_name, measures in centrality_measures.items():
                if node_id in measures:
                    node_analytics[f'{measure_name}_score'] = measures[node_id]
            
            return node_analytics
            
        except Exception as e:
            logger.error(f"Error getting node analytics: {e}")
            return {'error': str(e)}

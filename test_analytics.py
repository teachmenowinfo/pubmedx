#!/usr/bin/env python3
"""
Test script to verify the Graph Analytics functionality
"""

import asyncio
import networkx as nx
from app.services.analytics_service import GraphAnalyticsService

def create_test_graph():
    """Create a test graph for analytics testing"""
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes (articles)
    articles = [
        {'pmid': '1', 'title': 'Seed Article', 'authors': ['Author A'], 'journal': 'Test Journal'},
        {'pmid': '2', 'title': 'Cited Article 1', 'authors': ['Author B'], 'journal': 'Journal B'},
        {'pmid': '3', 'title': 'Cited Article 2', 'authors': ['Author C'], 'journal': 'Journal C'},
        {'pmid': '4', 'title': 'Reference Article 1', 'authors': ['Author D'], 'journal': 'Journal D'},
        {'pmid': '5', 'title': 'Reference Article 2', 'authors': ['Author E'], 'journal': 'Journal E'},
        {'pmid': '6', 'title': 'Bridge Article', 'authors': ['Author F'], 'journal': 'Journal F'},
        {'pmid': '7', 'title': 'Isolated Article', 'authors': ['Author G'], 'journal': 'Journal G'},
    ]
    
    for article in articles:
        G.add_node(article['pmid'], **article)
    
    # Add edges (citations)
    edges = [
        ('1', '2', 'cites'),      # Seed cites Article 2
        ('1', '3', 'cites'),      # Seed cites Article 3
        ('4', '1', 'cited_by'),   # Article 4 cites seed
        ('5', '1', 'cited_by'),   # Article 5 cites seed
        ('6', '2', 'cites'),      # Bridge article cites Article 2
        ('2', '6', 'cited_by'),   # Article 2 cites bridge
        ('3', '6', 'cited_by'),   # Article 3 cites bridge
    ]
    
    for source, target, rel_type in edges:
        G.add_edge(source, target, relationship_type=rel_type)
    
    return G

async def test_analytics_service():
    """Test the analytics service with a sample graph"""
    print("Testing Graph Analytics Service...")
    print("="*50)
    
    # Create test graph
    test_graph = create_test_graph()
    print(f"Created test graph with {test_graph.number_of_nodes()} nodes and {test_graph.number_of_edges()} edges")
    
    # Initialize analytics service
    analytics_service = GraphAnalyticsService()
    
    # Test comprehensive analysis
    print("\n1. Running comprehensive graph analysis...")
    try:
        analytics = analytics_service.analyze_graph(test_graph)
        
        if 'error' in analytics:
            print(f"❌ Analysis failed: {analytics['error']}")
            return
        
        print("✅ Analysis completed successfully!")
        
        # Display key results
        if 'summary' in analytics:
            summary = analytics['summary']
            print(f"\n📊 Summary:")
            if 'key_metrics' in summary:
                metrics = summary['key_metrics']
                print(f"   Total Articles: {metrics.get('total_articles', 'N/A')}")
                print(f"   Total Connections: {metrics.get('total_connections', 'N/A')}")
                print(f"   Network Density: {metrics.get('network_density', 'N/A'):.4f}")
                print(f"   Is Connected: {metrics.get('is_connected', 'N/A')}")
        
        if 'basic_statistics' in analytics:
            stats = analytics['basic_statistics']
            print(f"\n📈 Basic Statistics:")
            print(f"   Average Degree: {stats.get('average_degree', 'N/A'):.2f}")
            print(f"   Max Degree: {stats.get('max_degree', 'N/A')}")
            print(f"   Min Degree: {stats.get('min_degree', 'N/A')}")
            print(f"   Number of Components: {stats.get('number_of_components', 'N/A')}")
        
        if 'centrality_measures' in analytics:
            centrality = analytics['centrality_measures']
            print(f"\n🎯 Centrality Measures:")
            
            if 'pagerank' in centrality and centrality['pagerank']:
                top_pagerank = max(centrality['pagerank'].items(), key=lambda x: x[1])
                print(f"   Top PageRank: PMID {top_pagerank[0]} ({top_pagerank[1]:.4f})")
            
            if 'betweenness_centrality' in centrality and centrality['betweenness_centrality']:
                top_betweenness = max(centrality['betweenness_centrality'].items(), key=lambda x: x[1])
                print(f"   Top Betweenness: PMID {top_betweenness[0]} ({top_betweenness[1]:.4f})")
        
        if 'clustering_analysis' in analytics:
            clustering = analytics['clustering_analysis']
            print(f"\n🔗 Clustering Analysis:")
            print(f"   Global Clustering: {clustering.get('global_clustering', 'N/A'):.4f}")
            print(f"   Number of Communities: {clustering.get('number_of_communities', 'N/A')}")
        
        if 'research_insights' in analytics:
            insights = analytics['research_insights']
            print(f"\n💡 Research Insights:")
            
            if 'top_influential_papers' in insights:
                print(f"   Top Influential Papers: {len(insights['top_influential_papers'])} found")
            
            if 'bridge_papers' in insights:
                print(f"   Bridge Papers: {len(insights['bridge_papers'])} found")
            
            if 'emerging_topics' in insights:
                print(f"   Emerging Topics: {len(insights['emerging_topics'])} found")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    # Test node-specific analytics
    print(f"\n2. Testing node-specific analytics...")
    try:
        node_analytics = analytics_service.get_node_analytics(test_graph, '1')  # Seed article
        
        if 'error' not in node_analytics:
            print(f"✅ Node analytics for PMID 1:")
            print(f"   Degree: {node_analytics.get('degree', 'N/A')}")
            print(f"   In-degree: {node_analytics.get('in_degree', 'N/A')}")
            print(f"   Out-degree: {node_analytics.get('out_degree', 'N/A')}")
            print(f"   Neighbors: {len(node_analytics.get('neighbors', []))}")
            print(f"   Predecessors: {len(node_analytics.get('predecessors', []))}")
            print(f"   Successors: {len(node_analytics.get('successors', []))}")
        else:
            print(f"❌ Node analytics failed: {node_analytics['error']}")
            
    except Exception as e:
        print(f"❌ Error during node analysis: {e}")
    
    print(f"\n✅ Analytics testing completed!")

if __name__ == "__main__":
    asyncio.run(test_analytics_service())

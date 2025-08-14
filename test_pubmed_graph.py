#!/usr/bin/env python3
"""
Test script for PubMed Knowledge Graph functionality
"""

import asyncio
import aiohttp
import json
from app.services.pubmed_service import PubMedService
from app.services.graph_service import GraphService

async def test_pubmed_service():
    """Test the PubMed service with a sample PMID"""
    print("Testing PubMed Service...")
    
    # Use a well-known PMID for testing (COVID-19 related paper)
    test_pmid = "32284615"  # "Clinical Characteristics of Coronavirus Disease 2019 in China"
    
    pubmed_service = PubMedService()
    
    print(f"Fetching details for PMID: {test_pmid}")
    
    # Get article details
    article_details = await pubmed_service.get_article_details(test_pmid)
    if article_details:
        print(f"✓ Article found: {article_details['title']}")
        
        # Handle authors properly
        if article_details['authors']:
            if isinstance(article_details['authors'][0], dict):
                # Authors are dictionaries with 'name' field
                author_names = [author.get('name', 'Unknown') for author in article_details['authors'][:3]]
            else:
                # Authors are strings
                author_names = article_details['authors'][:3]
            print(f"  Authors: {', '.join(author_names)}...")
        else:
            print("  Authors: Not available")
            
        print(f"  Journal: {article_details['journal']}")
        print(f"  Published: {article_details['pubdate']}")
    else:
        print("✗ Failed to fetch article details")
        return
    
    # Get relationships
    print("\nFetching article relationships...")
    relationships = await pubmed_service.get_article_relationships(test_pmid)
    
    print(f"✓ References (cites): {len(relationships['references'])} articles")
    print(f"✓ Citations (cited by): {len(relationships['citations'])} articles")
    
    if relationships['references']:
        print(f"  Sample references: {relationships['references'][:5]}")
    if relationships['citations']:
        print(f"  Sample citations: {relationships['citations'][:5]}")
    
    return test_pmid, article_details, relationships

async def test_graph_service():
    """Test the graph service"""
    print("\n" + "="*50)
    print("Testing Graph Service...")
    
    test_pmid = "32284615"
    graph_service = GraphService()
    
    # Create a test graph
    graph_id = "test-graph-001"
    graph_info = graph_service.create_graph(graph_id, test_pmid)
    print(f"✓ Created graph: {graph_info}")
    
    # Build the graph (limited depth for testing)
    print("Building graph (depth 1)...")
    result = await graph_service.build_graph(graph_id, max_depth=1)
    print(f"✓ Graph built: {result}")
    
    # Get graph data
    graph_data = graph_service.get_graph_data(graph_id)
    if graph_data:
        print(f"✓ Graph data retrieved:")
        print(f"  Nodes: {len(graph_data['nodes'])}")
        print(f"  Edges: {len(graph_data['edges'])}")
        print(f"  Seed PMID: {graph_data['metadata']['seed_pmid']}")
        
        # Show some sample nodes
        print("\nSample nodes:")
        for i, node in enumerate(graph_data['nodes'][:3]):
            print(f"  {i+1}. PMID {node['id']}: {node['title'][:50]}...")
    
    return graph_data

async def main():
    """Main test function"""
    print("PubMed Knowledge Graph Test")
    print("="*50)
    
    try:
        # Test PubMed service
        await test_pubmed_service()
        
        # Test graph service
        graph_data = await test_graph_service()
        
        print("\n" + "="*50)
        print("✓ All tests completed successfully!")
        print("\nTo use the web interface:")
        print("1. Open http://localhost:8000 in your browser")
        print("2. Enter a PMID (e.g., 32284615)")
        print("3. Select depth and click 'Generate Graph'")
        print("4. Wait for the graph to build and explore!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 
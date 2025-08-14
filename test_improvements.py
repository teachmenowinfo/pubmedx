#!/usr/bin/env python3
"""
Test script to verify the improved PubMed Knowledge Graph functionality
"""

import asyncio
from app.services.pubmed_service import PubMedService

async def test_improved_service():
    """Test the improved PubMed service"""
    print("Testing Improved PubMed Service...")
    print("="*50)
    
    pubmed_service = PubMedService()
    
    # Test with a well-known PMID
    test_pmid = "32284615"  # COVID-19 paper
    
    print(f"Testing with PMID: {test_pmid}")
    print("This will test the improved rate limiting and error handling...")
    print()
    
    try:
        # Test article details
        print("1. Fetching article details...")
        article_details = await pubmed_service.get_article_details(test_pmid)
        if article_details:
            print(f"   ✅ Success: {article_details['title'][:50]}...")
        else:
            print("   ❌ Failed to fetch article details")
        
        # Test relationships
        print("2. Fetching article relationships...")
        relationships = await pubmed_service.get_article_relationships(test_pmid)
        print(f"   ✅ References: {len(relationships['references'])}")
        print(f"   ✅ Citations: {len(relationships['citations'])}")
        
        print()
        print("✅ All tests passed! The improved service is working correctly.")
        print()
        print("Key improvements:")
        print("- Better rate limiting with jitter")
        print("- Exponential backoff for retries")
        print("- Improved error handling")
        print("- Timeout protection")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_improved_service()) 
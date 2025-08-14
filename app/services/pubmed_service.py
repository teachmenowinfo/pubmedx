import asyncio
import aiohttp
import time
from typing import List, Dict, Optional, Set
from urllib.parse import quote
import logging
import random

logger = logging.getLogger(__name__)

class PubMedService:
    """Service for interacting with PubMed API via NCBI E-utilities"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    RATE_LIMIT_DELAY = 0.5  # Increased delay to be more conservative
    MAX_RETRIES = 3
    
    def __init__(self):
        self.last_request_time = 0
        
    async def _rate_limit(self):
        """Ensure we don't exceed rate limits with jitter"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Add some jitter to avoid thundering herd
        jitter = random.uniform(0, 0.1)
        required_delay = self.RATE_LIMIT_DELAY + jitter
        
        if time_since_last < required_delay:
            await asyncio.sleep(required_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    async def _make_request(self, session: aiohttp.ClientSession, url: str, retries: int = 0) -> Optional[Dict]:
        """Make a rate-limited request to NCBI API with retry logic"""
        await self._rate_limit()
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 429 and retries < self.MAX_RETRIES:
                    # Rate limited - wait longer and retry
                    wait_time = (2 ** retries) + random.uniform(0, 1)
                    logger.warning(f"Rate limited, waiting {wait_time:.2f}s before retry {retries + 1}")
                    await asyncio.sleep(wait_time)
                    return await self._make_request(session, url, retries + 1)
                else:
                    logger.error(f"API request failed: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error("Request timeout")
            return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            if retries < self.MAX_RETRIES:
                wait_time = (2 ** retries) + random.uniform(0, 1)
                logger.warning(f"Retrying in {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)
                return await self._make_request(session, url, retries + 1)
            return None
    
    async def get_article_details(self, pmid: str) -> Optional[Dict]:
        """Fetch article details by PMID"""
        url = f"{self.BASE_URL}/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        
        async with aiohttp.ClientSession() as session:
            response = await self._make_request(session, url)
            if response:
                try:
                    import json
                    data = json.loads(response)
                    if 'result' in data and pmid in data['result']:
                        article = data['result'][pmid]
                        article_data = {
                            'pmid': pmid,
                            'title': article.get('title', ''),
                            'authors': article.get('authors', []),
                            'journal': article.get('fulljournalname', ''),
                            'pubdate': article.get('pubdate', ''),
                            'abstract': article.get('abstract', ''),
                            'doi': article.get('elocationid', ''),
                            'last_updated': article.get('lastauthor', '')
                        }
                        
                        # Print CLI data snippet
                        print(f"📄 PMID {pmid}: {article_data['title'][:60]}...")
                        if article_data['authors']:
                            if isinstance(article_data['authors'][0], dict):
                                author_names = [author.get('name', 'Unknown') for author in article_data['authors'][:2]]
                            else:
                                author_names = article_data['authors'][:2]
                            print(f"   👥 Authors: {', '.join(author_names)}{'...' if len(article_data['authors']) > 2 else ''}")
                        print(f"   📚 Journal: {article_data['journal']}")
                        print(f"   📅 Published: {article_data['pubdate']}")
                        
                        return article_data
                except Exception as e:
                    logger.error(f"Error parsing article details: {e}")
            return None
    
    async def get_references(self, pmid: str) -> List[str]:
        """Get PMIDs of articles that this article references"""
        url = f"{self.BASE_URL}/elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&linkname=pubmed_pubmed_refs&retmode=json"
        
        async with aiohttp.ClientSession() as session:
            response = await self._make_request(session, url)
            if response:
                try:
                    import json
                    data = json.loads(response)
                    if 'linksets' in data and len(data['linksets']) > 0:
                        linkset = data['linksets'][0]
                        if 'linksetdbs' in linkset and len(linkset['linksetdbs']) > 0:
                            references = [str(ref) for ref in linkset['linksetdbs'][0].get('links', [])]
                            print(f"   📖 References: {len(references)} articles")
                            if references:
                                print(f"      Sample: {', '.join(references[:3])}{'...' if len(references) > 3 else ''}")
                            return references
                except Exception as e:
                    logger.error(f"Error parsing references: {e}")
            return []
    
    async def get_citations(self, pmid: str) -> List[str]:
        """Get PMIDs of articles that cite this article"""
        url = f"{self.BASE_URL}/elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&linkname=pubmed_pubmed_citedin&retmode=json"
        
        async with aiohttp.ClientSession() as session:
            response = await self._make_request(session, url)
            if response:
                try:
                    import json
                    data = json.loads(response)
                    if 'linksets' in data and len(data['linksets']) > 0:
                        linkset = data['linksets'][0]
                        if 'linksetdbs' in linkset and len(linkset['linksetdbs']) > 0:
                            citations = [str(citation) for citation in linkset['linksetdbs'][0].get('links', [])]
                            print(f"   📚 Citations: {len(citations)} articles")
                            if citations:
                                print(f"      Sample: {', '.join(citations[:3])}{'...' if len(citations) > 3 else ''}")
                            return citations
                except Exception as e:
                    logger.error(f"Error parsing citations: {e}")
            return []
    
    async def get_article_relationships(self, pmid: str) -> Dict:
        """Get both references and citations for an article"""
        print(f"\n🔍 Fetching relationships for PMID {pmid}...")
        references, citations = await asyncio.gather(
            self.get_references(pmid),
            self.get_citations(pmid)
        )
        
        print(f"   ✅ Total connections: {len(references) + len(citations)}")
        print()
        
        return {
            'pmid': pmid,
            'references': references,
            'citations': citations
        } 
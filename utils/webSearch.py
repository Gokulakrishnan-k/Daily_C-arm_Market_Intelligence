import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class WebSearchClient:
    """
    Free web search client using DuckDuckGo
    No API key required!
    """
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search_news(
        self,
        query: str,
        max_results: int = 10,
        time_period: str = "w"  # d=day, w=week, m=month
    ) -> List[Dict]:
        """
        Search for news articles using DuckDuckGo
        
        Args:
            query: Search query string
            max_results: Number of results to return
            time_period: Time period (d=day, w=week, m=month)
        
        Returns:
            List of article dictionaries
        """
        try:
            # Use DuckDuckGo news search
            results = list(self.ddgs.news(
                keywords=query,
                region="us-en",
                safesearch="moderate",
                timelimit=time_period,
                max_results=max_results
            ))
            
            articles = []
            for result in results:
                article = {
                    "title": result.get("title", ""),
                    "link": result.get("url", ""),
                    "snippet": result.get("body", ""),
                    "source": result.get("source", ""),
                    "date": result.get("date", ""),
                    "image": result.get("image", ""),
                    "query_category": query
                }
                articles.append(article)
            
            logger.info(f"Found {len(articles)} articles for: {query[:50]}...")
            
            # Be nice to DuckDuckGo - add small delay between requests
            time.sleep(1)
            
            return articles
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []
    
    def search_web(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        General web search using DuckDuckGo
        
        Args:
            query: Search query string
            max_results: Number of results to return
        
        Returns:
            List of result dictionaries
        """
        try:
            results = list(self.ddgs.text(
                keywords=query,
                region="us-en",
                safesearch="moderate",
                max_results=max_results
            ))
            
            items = []
            for result in results:
                item = {
                    "title": result.get("title", ""),
                    "link": result.get("href", ""),
                    "snippet": result.get("body", ""),
                }
                items.append(item)
            
            time.sleep(1)
            return items
            
        except Exception as e:
            logger.error(f"DuckDuckGo web search failed: {e}")
            return []
    
    def search_multiple_topics(
        self,
        topics: Dict[str, List[str]],
        results_per_query: int = 8
    ) -> Dict[str, List[Dict]]:
        """
        Search for multiple topics and organize results by category
        
        Args:
            topics: Dictionary of category -> list of keywords
            results_per_query: Number of results per query
        
        Returns:
            Dictionary of category -> list of articles
        """
        all_results = {}
        
        for category, keywords in topics.items():
            category_articles = []
            seen_links = set()
            
            logger.info(f"Searching category: {category}")
            
            for keyword in keywords:
                articles = self.search_news(
                    query=keyword,
                    max_results=results_per_query,
                    time_period="w"  # Last week
                )
                
                # Deduplicate articles by link
                for article in articles:
                    link = article.get("link", "")
                    if link and link not in seen_links:
                        seen_links.add(link)
                        article["category"] = category
                        category_articles.append(article)
            
            all_results[category] = category_articles
            logger.info(f"Category '{category}': {len(category_articles)} unique articles")
        
        return all_results
    
    def search_for_verification(
        self,
        claim: str,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Search for sources to verify a claim
        
        Args:
            claim: The claim to verify
            max_results: Number of results to return
        
        Returns:
            List of verification sources
        """
        # Add verification-focused keywords
        verification_query = f"{claim} source official announcement"
        return self.search_web(verification_query, max_results)

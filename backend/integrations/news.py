"""
News API Integration
Handles news data retrieval for cultural context
"""

import aiohttp
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class NewsAPIIntegration:
    """Integration with NewsAPI for current news"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
    
    async def get_cultural_news(self, country: str, language: str = "en") -> Optional[List[Dict]]:
        """Get cultural news for a country"""
        try:
            headers = {"X-API-Key": self.api_key}
            
            # Multiple search queries for comprehensive coverage
            queries = [
                f"{country} culture",
                f"{country} traditions",
                f"{country} festivals",
                f"{country} music",
                f"{country} food"
            ]
            
            all_articles = []
            
            async with aiohttp.ClientSession() as session:
                for query in queries:
                    params = {
                        "q": query,
                        "language": language,
                        "sortBy": "publishedAt",
                        "pageSize": 3
                    }
                    
                    async with session.get(
                        f"{self.base_url}/everything",
                        headers=headers,
                        params=params
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            articles = result.get("articles", [])
                            all_articles.extend(articles)
            
            # Remove duplicates and return top results
            unique_articles = []
            seen_urls = set()
            
            for article in all_articles:
                if article["url"] not in seen_urls and article["title"] != "[Removed]":
                    unique_articles.append(article)
                    seen_urls.add(article["url"])
            
            return unique_articles[:5]
            
        except Exception as e:
            logger.error(f"Error getting cultural news: {str(e)}")
            return None
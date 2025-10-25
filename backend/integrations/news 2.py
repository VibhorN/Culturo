"""
NewsAPI Integration
"""

import aiohttp
import logging

logger = logging.getLogger(__name__)

class NewsAPIIntegration:
    """Integration with NewsAPI for current news"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
    
    async def get_cultural_news(self, country, language="en"):
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
    
    async def get_top_headlines(self, q=None, country=None, language="en"):
        """Get top headlines"""
        try:
            headers = {"X-API-Key": self.api_key}
            params = {"language": language, "pageSize": 5}
            
            if q:
                params["q"] = q
            if country:
                params["country"] = country
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/top-headlines",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("articles", [])
                    else:
                        logger.error(f"NewsAPI error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting headlines: {str(e)}")
            return []

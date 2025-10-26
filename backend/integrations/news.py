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
            if not self.api_key:
                logger.warning("NewsAPI key not configured")
                return None
                
            headers = {"X-API-Key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                # Use everything endpoint with country-specific queries
                # Country-specific city/capital additions for better results
                country_capitals = {
                    "Japan": "Tokyo",
                    "France": "Paris", 
                    "Italy": "Rome",
                    "Spain": "Madrid",
                    "Mexico": "Mexico City",
                    "India": "New Delhi",
                    "China": "Beijing",
                    "Thailand": "Bangkok",
                    "Germany": "Berlin"
                }
                
                capital = country_capitals.get(country, "")
                
                queries = [
                    f"{country} {capital}" if capital else f"{country}",  # Country + capital
                    f"{country} latest news",  # Latest news
                    f"breaking news {country}"  # Breaking news
                ]
                
                all_articles = []
                used_urls = set()
                
                for query in queries:
                    params = {
                        "q": query,
                        "language": language,
                        "sortBy": "publishedAt",
                        "pageSize": 5
                    }
                    
                    async with session.get(
                        f"{self.base_url}/everything",
                        headers=headers,
                        params=params
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            articles = result.get("articles", [])
                            
                            # Add unique articles
                            for article in articles:
                                url = article.get("url", "")
                                if url and url not in used_urls and article.get("title") != "[Removed]":
                                    all_articles.append(article)
                                    used_urls.add(url)
                
                if all_articles:
                    logger.info(f"✅ Got {len(all_articles)} news articles for {country}")
                    return all_articles[:10]  # Return up to 10 articles
                else:
                    logger.warning(f"No valid news articles found for {country}")
                    return None
            
        except Exception as e:
            logger.error(f"Error getting cultural news: {str(e)}")
            return None
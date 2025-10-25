"""
Data Retrieval Agent
Decides which APIs to call and retrieves relevant data
"""

import json
import logging
import aiohttp
import time
from typing import Dict, List, Optional
from core.base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

# Import logging system
try:
    from utils.logging import log_api_call
except ImportError:
    def log_api_call(*args, **kwargs):
        pass

# Import integrations
try:
    from integrations import NewsAPIIntegration, SpotifyIntegration, TripAdvisorIntegration
except ImportError:
    logger.warning("Could not import integrations - using placeholder implementations")


class DataRetrievalAgent(BaseAgent):
    """
    Intelligent data retrieval agent that:
    1. Analyzes what data the user wants
    2. Decides which APIs to call
    3. Asks for clarification when needed
    4. Retrieves and formats the data
    """
    
    def __init__(self, anthropic_api_key: str, news_api_key: str = None, spotify_client_id: str = None, spotify_client_secret: str = None, tripadvisor_api_key: str = None):
        super().__init__("DataRetrieval", anthropic_api_key)
        
        # Initialize integrations
        self.news_integration = NewsAPIIntegration(news_api_key) if news_api_key else None
        self.spotify_integration = SpotifyIntegration(spotify_client_id, spotify_client_secret) if spotify_client_id and spotify_client_secret else None
        self.tripadvisor_integration = TripAdvisorIntegration(tripadvisor_api_key) if tripadvisor_api_key else None
        
        self.available_apis = {
            "news": self._get_news_data,
            "music": self._get_music_data,
            "landmarks": self._get_landmarks_data,
            "restaurants": self._get_restaurants_data,
            "destinations": self._get_destinations_data,
            "food": self._get_food_data,  # Placeholder for future
            "movies": self._get_movies_data,  # Placeholder for future
            "government": self._get_government_data,  # Placeholder for future
            "festivals": self._get_festivals_data,  # Placeholder for future
        }
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Main processing function for data retrieval
        """
        try:
            country = input_data.get("country", "")
            query = input_data.get("query", "")
            context = input_data.get("context", {})
            
            logger.info(f"[DataRetrieval] Processing query for {country}: {query}")
            
            # Step 1: Analyze what data the user wants
            data_analysis = await self._analyze_data_needs(query, country, context)
            
            # Step 2: Check if we need clarification
            if data_analysis.get("needs_clarification", False):
                return AgentResponse(
                    agent_name=self.name,
                    status="clarification_needed",
                    data={
                        "clarification_question": data_analysis["clarification_question"],
                        "suggested_options": data_analysis.get("suggested_options", [])
                    },
                    confidence=0.9,
                    reasoning="User query is ambiguous, need clarification"
                )
            
            # Step 3: Retrieve the requested data
            retrieved_data = await self._retrieve_data(data_analysis, country)
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data=retrieved_data,
                confidence=data_analysis.get("confidence", 0.8),
                reasoning=data_analysis.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"[DataRetrieval] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _analyze_data_needs(self, query: str, country: str, context: Dict) -> Dict:
        """Use Claude to analyze what data the user wants"""
        try:
            prompt = f"""
            You are a data retrieval specialist. Analyze this user query to determine what specific data they want.
            
            User Query: "{query}"
            Country: "{country}"
            Context: {json.dumps(context)}
            
            Available data sources:
            - news: Current news and events
            - food: Food recommendations and cuisine information
            - movies: Movies and entertainment
            - music: Music and cultural music
            - government: Government and political information
            - festivals: Festivals and cultural events
            
            Determine:
            1. What specific data does the user want? (be very specific)
            2. Which data sources are most relevant?
            3. Is the query clear enough, or do we need clarification?
            4. If clarification is needed, what should we ask?
            5. Confidence level (0-1)
            
            Examples:
            - "I'm interested in Japan" → needs_clarification: true, ask what aspect
            - "Tell me about Japanese food" → clear, use food API
            - "What's happening in Japan?" → clear, use news API
            - "Japanese culture" → needs_clarification: true, ask what aspect
            
            Respond in JSON:
            {{
                "data_sources_needed": ["news", "food"],
                "specific_request": "User wants Japanese food recommendations",
                "needs_clarification": false,
                "clarification_question": "",
                "suggested_options": [],
                "confidence": 0.9,
                "reasoning": "Query is clear and specific"
            }}
            """
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    execution_time = time.time() - start_time
                    
                    # Log API call
                    log_api_call(
                        service="anthropic",
                        endpoint="/v1/messages",
                        method="POST",
                        request_data=data,
                        response_data={"status": response.status, "content": "..."},
                        status_code=response.status,
                        execution_time=execution_time
                    )
                    
                    if response.status == 200:
                        result = await response.json()
                        analysis_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            # Extract JSON from response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                analysis = json.loads(analysis_text[start_idx:end_idx])
                logger.info(f"[DataRetrieval] Analysis: {analysis}")
                return analysis
                    
        except Exception as e:
            logger.error(f"[DataRetrieval] Error analyzing data needs: {str(e)}")
        
        # Fallback analysis
        return {
            "data_sources_needed": ["news"],
            "specific_request": "General information request",
            "needs_clarification": True,
            "clarification_question": f"What specific aspect of {country} are you most interested in?",
            "suggested_options": ["Current news", "Food recommendations", "Cultural events", "General overview"],
            "confidence": 0.3,
            "reasoning": "Fallback analysis due to error"
        }
    
    async def _retrieve_data(self, analysis: Dict, country: str) -> Dict:
        """Retrieve data from the specified sources"""
        retrieved_data = {}
        data_sources = analysis.get("data_sources_needed", [])
        
        for source in data_sources:
            if source in self.available_apis:
                try:
                    data = await self.available_apis[source](country)
                    retrieved_data[source] = data
                    logger.info(f"[DataRetrieval] Retrieved {source} data for {country}")
                except Exception as e:
                    logger.error(f"[DataRetrieval] Error retrieving {source} data: {str(e)}")
                    retrieved_data[source] = {"error": str(e)}
            else:
                logger.warning(f"[DataRetrieval] Unknown data source: {source}")
        
        return retrieved_data
    
    async def _get_news_data(self, country: str) -> Dict:
        """Get news data for the country using NewsAPI"""
        try:
            if self.news_integration:
                articles = await self.news_integration.get_cultural_news(country)
                if articles:
                    return {
                        "country": country,
                        "articles": articles,
                        "total_results": len(articles),
                        "source": "news_api",
                        "timestamp": "now"
                    }
            
            # Fallback data
            return {
                "country": country,
                "articles": [
                    {
                        "title": f"Latest news from {country}",
                        "description": f"Here are the current events happening in {country}",
                        "url": "#",
                        "source": "NewsAPI"
                    }
                ],
                "source": "news_api_fallback",
                "timestamp": "now"
            }
        except Exception as e:
            logger.error(f"[DataRetrieval] Error getting news data: {str(e)}")
            return {"error": str(e)}
    
    async def _get_music_data(self, country: str) -> Dict:
        """Get music data for the country using Spotify"""
        try:
            if self.spotify_integration:
                playlists = await self.spotify_integration.search_playlists(country, limit=5)
                if playlists:
                    return {
                        "country": country,
                        "playlists": playlists,
                        "total_results": len(playlists),
                        "source": "spotify_api",
                        "timestamp": "now"
                    }
            
            # Fallback data
            return {
                "country": country,
                "playlists": [
                    {
                        "name": f"Popular Music from {country}",
                        "description": f"Trending music and artists from {country}",
                        "tracks": {"total": 50}
                    }
                ],
                "source": "spotify_api_fallback",
                "timestamp": "now"
            }
        except Exception as e:
            logger.error(f"[DataRetrieval] Error getting music data: {str(e)}")
            return {"error": str(e)}
    
    async def _get_landmarks_data(self, country: str) -> Dict:
        """Get historical landmarks for the country using TripAdvisor"""
        try:
            if self.tripadvisor_integration:
                landmarks = await self.tripadvisor_integration.get_historical_landmarks(country, limit=5)
                if landmarks:
                    return landmarks
            
            # Fallback data
            return {
                "country": country,
                "category": "attractions",
                "locations": [
                    {
                        "name": f"Historical Landmarks in {country}",
                        "description": f"Famous historical sites and monuments in {country}"
                    }
                ],
                "source": "tripadvisor_api_fallback",
                "timestamp": "now"
            }
        except Exception as e:
            logger.error(f"[DataRetrieval] Error getting landmarks data: {str(e)}")
            return {"error": str(e)}
    
    async def _get_restaurants_data(self, country: str) -> Dict:
        """Get popular restaurants for the country using TripAdvisor"""
        try:
            if self.tripadvisor_integration:
                restaurants = await self.tripadvisor_integration.get_popular_restaurants(country, limit=5)
                if restaurants:
                    return restaurants
            
            # Fallback data
            return {
                "country": country,
                "category": "restaurants",
                "locations": [
                    {
                        "name": f"Traditional Restaurants in {country}",
                        "description": f"Popular local cuisine and dining spots in {country}"
                    }
                ],
                "source": "tripadvisor_api_fallback",
                "timestamp": "now"
            }
        except Exception as e:
            logger.error(f"[DataRetrieval] Error getting restaurants data: {str(e)}")
            return {"error": str(e)}
    
    async def _get_destinations_data(self, country: str) -> Dict:
        """Get tourist destinations for the country using TripAdvisor"""
        try:
            if self.tripadvisor_integration:
                destinations = await self.tripadvisor_integration.get_tourist_destinations(country, limit=5)
                if destinations:
                    return destinations
            
            # Fallback data
            return {
                "country": country,
                "category": "attractions",
                "locations": [
                    {
                        "name": f"Must-Visit Destinations in {country}",
                        "description": f"Top tourist attractions and places to visit in {country}"
                    }
                ],
                "source": "tripadvisor_api_fallback",
                "timestamp": "now"
            }
        except Exception as e:
            logger.error(f"[DataRetrieval] Error getting destinations data: {str(e)}")
            return {"error": str(e)}
    
    async def _get_food_data(self, country: str) -> Dict:
        """Get food data for the country (placeholder)"""
        return {
            "country": country,
            "message": "Food API not yet implemented",
            "source": "food_api"
        }
    
    async def _get_movies_data(self, country: str) -> Dict:
        """Get movies data for the country (placeholder)"""
        return {
            "country": country,
            "message": "Movies API not yet implemented",
            "source": "movies_api"
        }
    
    async def _get_government_data(self, country: str) -> Dict:
        """Get government data for the country (placeholder)"""
        return {
            "country": country,
            "message": "Government API not yet implemented",
            "source": "government_api"
        }
    
    async def _get_festivals_data(self, country: str) -> Dict:
        """Get festivals data for the country (placeholder)"""
        return {
            "country": country,
            "message": "Festivals API not yet implemented",
            "source": "festivals_api"
        }

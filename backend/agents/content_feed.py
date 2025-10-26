"""
Content Feed Agent
Generates cultural content feed using real APIs
"""

import json
import logging
import aiohttp
import time
import os
from typing import Dict, List
from .base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

try:
    from utils.logging import log_api_call
except ImportError:
    def log_api_call(*args, **kwargs):
        pass


class ContentFeedAgent(BaseAgent):
    """
    Generates cultural content feed by calling real integrations
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("ContentFeed", anthropic_api_key)
        # Initialize integrations
        self._init_integrations()
    
    def _init_integrations(self):
        """Initialize API integrations"""
        try:
            from integrations.news import NewsAPIIntegration
            from integrations.spotify import SpotifyIntegration
            from integrations.tripadvisor import TripAdvisorIntegration
            from integrations.tmdb import TMDBIntegration
            
            # Get API keys from environment
            self.news_api = NewsAPIIntegration(os.getenv('NEWS_API_KEY'))
            self.spotify_api = SpotifyIntegration(
                os.getenv('SPOTIFY_CLIENT_ID'),
                os.getenv('SPOTIFY_CLIENT_SECRET')
            )
            self.tripadvisor_api = TripAdvisorIntegration(os.getenv('TRIPADVISOR_API_KEY'))
            self.tmdb_api = TMDBIntegration(os.getenv('TMDB_API_KEY'))
            
            logger.info("ContentFeedAgent initialized with all integrations")
        except Exception as e:
            logger.warning(f"Could not initialize some integrations: {e}")
            self.news_api = None
            self.spotify_api = None
            self.tripadvisor_api = None
            self.tmdb_api = None
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """Generate content feed based on country and interests"""
        try:
            country = input_data.get("country", "")
            interests = input_data.get("interests", ["news", "songs", "movies", "monuments", "food"])
            
            logger.info(f"[ContentFeed] Generating feed for {country} with interests: {interests}")
            
            cards = []
            
            # Generate cards for each interest type
            if "movies" in interests or "movie" in interests:
                movie_cards = await self._get_movie_cards(country)
                cards.extend(movie_cards[:3])  # Max 3 movies
            
            if "news" in interests:
                news_cards = await self._get_news_cards(country)
                cards.extend(news_cards[:5])  # Max 5 news
            
            if "songs" in interests or "music" in interests:
                music_card = await self._get_music_card(country)
                if music_card:
                    cards.append(music_card)
            
            if "food" in interests or "restaurants" in interests:
                food_cards = await self._get_food_cards(country)
                cards.extend(food_cards[:2])  # Max 2 food
            
            if "monuments" in interests or "attractions" in interests or "landmarks" in interests:
                attraction_cards = await self._get_attraction_cards(country)
                cards.extend(attraction_cards[:2])  # Max 2 attractions
            
            # Ensure minimum 7 cards
            while len(cards) < 7:
                additional_news = await self._get_news_cards(country)
                if additional_news and len(cards) < 10:
                    cards.extend(additional_news[:1])
                else:
                    break
            
            logger.info(f"[ContentFeed] Generated {len(cards)} total cards")
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data={"cards": cards, "total_cards": len(cards)},
                confidence=0.9,
                reasoning=f"Generated {len(cards)} cards for {country}"
            )
            
        except Exception as e:
            logger.error(f"[ContentFeed] Error: {e}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _get_movie_cards(self, country: str) -> List[Dict]:
        """Get movie cards using TMDB for trailers"""
        cards = []
        try:
            # Use Claude to suggest movies
            prompt = f"""
            Suggest 3 specific popular movies from {country} that are culturally significant.
            Be very specific with exact movie titles. Return ONLY the movie titles, one per line.
            Do not include numbering or other text, just the titles.
            """
            
            movie_titles = await self._call_claude(prompt)
            movie_list = [line.strip() for line in movie_titles.split('\n') if line.strip()][:3]
            
            for title in movie_list:
                # Get real trailer link using TMDB
                trailer_link = None
                if self.tmdb_api:
                    try:
                        trailer_link = await self.tmdb_api.get_movie_trailer(title)
                        if trailer_link:
                            logger.info(f"✅ Got real trailer URL for {title}: {trailer_link}")
                    except Exception as e:
                        logger.warning(f"Could not get trailer for {title}: {e}")
                
                # Fallback to YouTube search if no trailer found
                if not trailer_link:
                    trailer_link = f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}+official+trailer"
                
                # Generate description
                description = await self._call_claude(f"""
                Write a 2-sentence description for the movie: {title} from {country}.
                Focus on its cultural significance and why it's important.
                Return ONLY the description, nothing else.
                """)
                
                cards.append({
                    "type": "movie",
                    "title": title,
                    "description": description.strip() or f"A culturally significant film from {country}",
                    "trailer_link": trailer_link,
                    "poster_url": None,
                    "index": len(cards)
                })
            
        except Exception as e:
            logger.error(f"Error getting movie cards: {e}")
            # Fallback
            cards.append({
                "type": "movie",
                "title": f"Popular movie from {country}",
                "description": f"A culturally significant film from {country}",
                "trailer_link": f"https://www.youtube.com/results?search_query={country}+movie+trailer",
                "index": 0
            })
        
        return cards
    
    async def _get_news_cards(self, country: str) -> List[Dict]:
        """Get news cards using NewsAPI and Claude with deduplication"""
        cards = []
        try:
            if self.news_api:
                articles = await self.news_api.get_cultural_news(country)
                if articles:
                    # Deduplicate articles by title
                    seen_titles = set()
                    unique_articles = []
                    for article in articles:
                        title = article.get('title', '').strip()
                        if title and title not in seen_titles and title != "[Removed]":
                            seen_titles.add(title)
                            unique_articles.append(article)
                    
                    # Process up to 5 unique articles
                    for i, article in enumerate(unique_articles[:5]):
                        # Generate a teaser using Claude
                        article_desc = article.get('description', '')[:200]
                        teaser = await self._call_claude(f"""
                        Create a 2-3 sentence, engaging teaser for this news article:
                        Title: {article.get('title', '')}
                        Content: {article_desc}
                        
                        Make it compelling and cultural. Return ONLY the teaser, nothing else.
                        """)
                        
                        cards.append({
                            "type": "news",
                            "title": article.get('title', f'News from {country}'),
                            "description": teaser.strip() or f"Recent cultural developments in {country}.",
                            "link": article.get('url', '#')
                        })
            
            # Fallback if no API or empty results - generate news using Claude
            if not cards:
                logger.info(f"NewsAPI unavailable, generating news content with Claude for {country}")
                # Get 3 news topics from Claude
                topics_prompt = f"""
                Generate 3 specific, recent cultural news headlines for {country}.
                Make them realistic and current (food trends, cultural events, music festivals, etc.).
                Return ONLY the headlines, one per line, nothing else.
                """
                topics = await self._call_claude(topics_prompt)
                headlines = [line.strip() for line in topics.split('\n') if line.strip()][:3]
                
                # Add fallback headlines if Claude fails
                if not headlines:
                    headlines = [
                        f"Cultural festivals celebrate {country}'s traditions",
                        f"New cuisine trends emerge in {country}",
                        f"Music and arts scene thrives in {country}"
                    ]
                
                # Generate descriptions and links
                for i, headline in enumerate(headlines):
                    desc = await self._call_claude(f"""
                    Write a 2-sentence description for this news headline about {country}: {headline}
                    Make it engaging and informative. Return ONLY the description.
                    """)
                    
                    cards.append({
                        "type": "news",
                        "title": headline,
                        "description": desc.strip() or f"Recent cultural developments in {country}.",
                        "link": f"https://www.google.com/search?q={headline.replace(' ', '+')}"
                    })
            
        except Exception as e:
            logger.error(f"Error getting news cards: {e}")
            if not cards:
                cards.append({
                    "type": "news",
                    "title": f"Latest from {country}",
                    "description": f"Current cultural events in {country}",
                    "link": "#"
                })
        
        return cards
    
    async def _get_music_card(self, country: str) -> Dict:
        """Get music card using Spotify"""
        try:
            if self.spotify_api:
                songs = await self.spotify_api.search_country_songs(country, limit=3)
                if songs:
                    # Map to expected format
                    formatted_songs = []
                    for song in songs:
                        formatted_songs.append({
                            "name": song.get("song_name", ""),
                            "artist": song.get("artist_name", ""),
                            "spotify_link": song.get("spotify_url", "#"),
                            "album_art": song.get("image_url", "")
                        })
                    
                    return {
                        "type": "music",
                        "country": country,
                        "songs": formatted_songs
                    }
            
            # Fallback
            return {
                "type": "music",
                "country": country,
                "songs": [
                    {"name": f"Popular song from {country}", "artist": "Artist", "spotify_link": "#", "album_art": ""},
                    {"name": f"Trending in {country}", "artist": "Local Artist", "spotify_link": "#", "album_art": ""},
                    {"name": f"Cultural music from {country}", "artist": "Traditional", "spotify_link": "#", "album_art": ""}
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting music card: {e}")
            return {
                "type": "music",
                "country": country,
                "songs": [{"name": "Music from " + country, "artist": "Artist", "spotify_link": "#", "album_art": ""}]
            }
    
    async def _get_food_cards(self, country: str) -> List[Dict]:
        """Get food cards using TripAdvisor with photos"""
        cards = []
        try:
            if self.tripadvisor_api:
                restaurants_data = await self.tripadvisor_api.get_popular_restaurants(country, limit=2)
                if restaurants_data and restaurants_data.get('locations'):
                    restaurants = restaurants_data['locations']
                    for rest in restaurants:
                        description = await self._call_claude(f"""
                        Create a mouth-watering one-sentence description for: {rest.get('name', '')}
                        in {country}.
                        
                        Return ONLY the description, nothing else.
                        """)
                        
                        cards.append({
                            "type": "food",
                            "restaurant_name": rest.get('name', f'Restaurant in {country}'),
                            "description": description.strip() or f"Delicious local cuisine in {country}",
                            "photo_url": rest.get('photo', ''),  # FIXED: Use 'photo' not 'description'
                            "website": "#",
                            "price_level": "$$",
                            "index": len(cards)
                        })
            
            # Fallback
            if not cards:
                for i in range(2):
                    cards.append({
                        "type": "food",
                        "restaurant_name": f"Popular restaurant in {country}",
                        "description": f"Mouth-watering local cuisine in {country}",
                        "photo_url": "",
                        "website": "#",
                        "price_level": "$$",
                        "index": i
                    })
            
        except Exception as e:
            logger.error(f"Error getting food cards: {e}")
            cards.append({
                "type": "food",
                "restaurant_name": f"Restaurant in {country}",
                "description": f"Amazing food in {country}",
                "photo_url": "",
                "website": "#",
                "price_level": "$$",
                "index": 0
            })
        
        return cards
    
    async def _get_attraction_cards(self, country: str) -> List[Dict]:
        """Get attraction cards using TripAdvisor with photos"""
        cards = []
        try:
            if self.tripadvisor_api:
                attractions_data = await self.tripadvisor_api.get_historical_landmarks(country, limit=2)
                if attractions_data and attractions_data.get('locations'):
                    attractions = attractions_data['locations']
                    for attr in attractions:
                        description = await self._call_claude(f"""
                        Describe the cultural significance of: {attr.get('name', '')} in {country}.
                        
                        Return ONLY the description, nothing else.
                        """)
                        
                        cards.append({
                            "type": "attraction",
                            "name": attr.get('name', f'Cultural site in {country}'),
                            "description": description.strip() or f"A significant cultural site in {country}",
                            "photo_url": attr.get('photo', ''),  # FIXED: Use 'photo' not 'description'
                            "cultural_significance": f"An important landmark in {country}",
                            "index": len(cards)
                        })
            
            # Fallback
            if not cards:
                for i in range(2):
                    cards.append({
                        "type": "attraction",
                        "name": f"Cultural attraction in {country}",
                        "description": f"A significant cultural site in {country}",
                        "photo_url": "",
                        "index": i
                    })
            
        except Exception as e:
            logger.error(f"Error getting attraction cards: {e}")
            cards.append({
                "type": "attraction",
                "name": f"Site in {country}",
                "description": f"Cultural site in {country}",
                "photo_url": "",
                "index": 0
            })
        
        return cards
    
    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API"""
        headers = {
            "x-api-key": self.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["content"][0]["text"]
                return ""


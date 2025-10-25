import os
import requests
import json
import asyncio
import aiohttp
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DeepgramIntegration:
    """Integration with Deepgram for multilingual speech-to-text"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.deepgram.com/v1"
    
    async def transcribe_audio(self, audio_data, language="en-US"):
        """Transcribe audio using Deepgram API"""
        try:
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav"
            }
            
            params = {
                "model": "nova-2",
                "language": language,
                "punctuate": True,
                "diarize": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/listen",
                    headers=headers,
                    params=params,
                    data=audio_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "transcript": result["results"]["channels"][0]["alternatives"][0]["transcript"],
                            "confidence": result["results"]["channels"][0]["alternatives"][0]["confidence"],
                            "language": language
                        }
                    else:
                        logger.error(f"Deepgram API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error in Deepgram transcription: {str(e)}")
            return None

class VapiIntegration:
    """Integration with Vapi for text-to-speech and voice interface"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.vapi.ai"
    
    async def synthesize_speech(self, text, voice="alloy", language="en"):
        """Synthesize speech using Vapi API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "voice": voice,
                "language": language,
                "speed": 1.0,
                "pitch": 1.0
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/voice/synthesize",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "audio_url": result.get("audio_url"),
                            "duration": result.get("duration"),
                            "language": language
                        }
                    else:
                        logger.error(f"Vapi API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error in Vapi synthesis: {str(e)}")
            return None

class SpotifyIntegration:
    """Integration with Spotify API for music data"""
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = 0  # Initialize to 0 instead of None
    
    async def get_access_token(self):
        """Get Spotify access token"""
        try:
            auth_url = "https://accounts.spotify.com/api/token"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            logger.info(f"Requesting Spotify token with client_id: {self.client_id[:10]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, data=auth_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.access_token = result["access_token"]
                        self.token_expires_at = datetime.now().timestamp() + result["expires_in"]
                        logger.info("Spotify token obtained successfully")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Spotify auth error: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error getting Spotify token: {str(e)}")
            return False
    
    async def search_playlists(self, country, limit=5):
        """Search for country-specific playlists"""
        try:
            if not self.access_token or datetime.now().timestamp() >= self.token_expires_at:
                await self.get_access_token()
            
            if not self.access_token:
                return None
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Search for country-specific playlists
            search_queries = [
                f"{country} music",
                f"{country} hits",
                f"{country} popular",
                f"music from {country}"
            ]
            
            all_playlists = []
            
            async with aiohttp.ClientSession() as session:
                for query in search_queries:
                    params = {
                        "q": query,
                        "type": "playlist",
                        "limit": limit
                    }
                    
                    async with session.get(
                        "https://api.spotify.com/v1/search",
                        headers=headers,
                        params=params
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            playlists = result.get("playlists", {}).get("items", [])
                            all_playlists.extend(playlists)
                            logger.info(f"Found {len(playlists)} playlists for query: {query}")
                        else:
                            error_text = await response.text()
                            logger.warning(f"Spotify search error for '{query}': {response.status} - {error_text}")
            
            # Remove duplicates and return top results
            unique_playlists = []
            seen_ids = set()
            
            logger.info(f"Total playlists found: {len(all_playlists)}")
            
            for playlist in all_playlists:
                if playlist and playlist.get("id") and playlist["id"] not in seen_ids:
                    unique_playlists.append(playlist)
                    seen_ids.add(playlist["id"])
            
            logger.info(f"Unique playlists after deduplication: {len(unique_playlists)}")
            return unique_playlists[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Spotify playlists: {str(e)}")
            return None

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

class RedditIntegration:
    """Integration with Reddit API for slang and cultural insights"""
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
    
    async def get_access_token(self):
        """Get Reddit access token"""
        try:
            auth_url = "https://www.reddit.com/api/v1/access_token"
            auth_data = {
                "grant_type": "client_credentials"
            }
            
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    auth_url,
                    data=auth_data,
                    auth=auth
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.access_token = result["access_token"]
                        return True
                    else:
                        logger.error(f"Reddit auth error: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error getting Reddit token: {str(e)}")
            return False
    
    async def get_cultural_posts(self, country, limit=10):
        """Get cultural posts from Reddit"""
        try:
            if not self.access_token:
                await self.get_access_token()
            
            if not self.access_token:
                return None
            
            headers = {"Authorization": f"bearer {self.access_token}"}
            
            # Search in relevant subreddits
            subreddits = [
                f"r/{country.lower()}",
                "r/culture",
                "r/languagelearning",
                "r/travel"
            ]
            
            all_posts = []
            
            async with aiohttp.ClientSession() as session:
                for subreddit in subreddits:
                    try:
                        async with session.get(
                            f"https://oauth.reddit.com/{subreddit}/hot",
                            headers=headers,
                            params={"limit": limit}
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                posts = result.get("data", {}).get("children", [])
                                all_posts.extend(posts)
                    except:
                        continue  # Skip if subreddit doesn't exist
            
            # Filter and return relevant posts
            relevant_posts = []
            for post in all_posts:
                post_data = post.get("data", {})
                title = post_data.get("title", "").lower()
                if any(keyword in title for keyword in ["culture", "language", "slang", "tradition", "food", "music"]):
                    relevant_posts.append({
                        "title": post_data.get("title"),
                        "selftext": post_data.get("selftext", "")[:200] + "...",
                        "url": f"https://reddit.com{post_data.get('permalink')}",
                        "score": post_data.get("score", 0),
                        "subreddit": post_data.get("subreddit")
                    })
            
            return relevant_posts[:5]
            
        except Exception as e:
            logger.error(f"Error getting Reddit posts: {str(e)}")
            return None

class ClaudeIntegration:
    """Integration with Anthropic Claude for AI reasoning"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1"
    
    async def synthesize_cultural_data(self, cultural_data, user_query=""):
        """Use Claude to synthesize cultural data into a coherent response"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Prepare the prompt for Claude
            prompt = f"""
            You are WorldWise, an AI cultural immersion companion. Based on the following cultural data about {cultural_data.get('country', 'a country')}, create a comprehensive cultural summary that includes:

            1. A warm, engaging introduction
            2. Key cultural insights from the data
            3. Practical phrases or expressions
            4. Cultural etiquette tips
            5. Recommendations for cultural immersion

            Cultural Data:
            {json.dumps(cultural_data, indent=2)}

            User Query: {user_query}

            Please respond in a conversational, educational tone that makes the user excited to explore this culture. Keep it concise but informative.
            """
            
            data = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "synthesis": result["content"][0]["text"],
                            "confidence": 0.9,
                            "sources": cultural_data
                        }
                    else:
                        logger.error(f"Claude API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error in Claude synthesis: {str(e)}")
            return None

class TripAdvisorIntegration:
    """Async integration with TripAdvisor Content API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.content.tripadvisor.com/api/v1/location"
        
        self.country_coordinate_mappings = {
            "France": {
                "latLong": "48.8566,2.3522",
                "radius": "5",
                "radiusUnit": "m"
            },
            "Spain": {
                "latLong": "40.4168,-3.7038",
                "radius": "2",
                "radiusUnit": "m"
            },
            "Japan": {
                "latLong": "35.6895,139.6917",
                "radius": "5",
                "radiusUnit": "m"
            }
        }

    async def get_popular_locations(self, country: str, category: str, searchQuery: str, limit: int = 10):
        """
        Get popular locations for a given country, category, and search term.
        Returns a list of dicts with name, description, and photo URL.
        """
        if (
            country not in self.country_coordinate_mappings
            or category not in ["restaurants", "hotels", "attractions"]
        ):
            return None

        location_params = self.country_coordinate_mappings[country]
        headers = {"Accept": "application/json"}
        params = {
            "key": self.api_key,
            "searchQuery": searchQuery,
            "category": category,
            **location_params
        }

        # Step 1: Retrieve location IDs
        locations = await self.retrieve_location_ids(headers, params)
        if not locations:
            return []

        results = []

        async with aiohttp.ClientSession() as session:
            tasks = [
                self.get_location_data(session, name, loc_id, headers)
                for name, loc_id in list(locations.items())[:limit]
            ]
            results = await asyncio.gather(*tasks)

        # Filter out None results
        return [r for r in results if r]

    async def retrieve_location_ids(self, headers, params):
        """Retrieve location IDs from TripAdvisor API asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/search", headers=headers, params=params) as response:
                    if response.status != 200:
                        logger.error(f"TripAdvisor API error: {response.status}")
                        return None
                    data = await response.json()
                    return {place["name"]: place["location_id"] for place in data.get("data", [])}
        except Exception as e:
            logger.error(f"Error retrieving location IDs: {str(e)}")
            return None

    async def get_location_data(self, session, name, location_id, headers):
        """Fetch details + photo for a single location."""
        try:
            # Fetch details and photo concurrently
            details_task = self.get_location_description(session, location_id, headers)
            photo_task = self.get_location_photo(session, location_id, headers)
            details, photo_url = await asyncio.gather(details_task, photo_task)

            if not details:
                return None

            return {
                "name": name,
                "location_id": location_id,
                "price_level": details.get("price_level"),
                "website": details.get("website"),
                "address": details.get("address_obj", {}).get("address_string"),
                "photo": photo_url
            }

        except Exception as e:
            logger.error(f"Error getting location data for {name}: {str(e)}")
            return None

    async def get_location_description(self, session, location_id: str, headers):
        """Async: Get the location’s description/details."""
        try:
            params = {"key": self.api_key}
            async with session.get(f"{self.base_url}/{location_id}/details", headers=headers, params=params) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                return data
        except Exception as e:
            logger.error(f"Error retrieving location description: {str(e)}")
            return None

    async def get_location_photo(self, session, location_id: str, headers):
        """Async: Get the first available photo for a given location."""
        try:
            params = {"key": self.api_key, "limit": 1}
            async with session.get(f"{self.base_url}/{location_id}/photos", headers=headers, params=params) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                photos = data.get("data", [])
                if not photos:
                    return None
                return photos[0].get("images", {}).get("large", {}).get("url")
        except Exception as e:
            logger.error(f"Error retrieving location photo: {str(e)}")
            return None

class TMDBIntegration:
    """Async integration with TMDb to fetch movie trailers."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    async def get_movie_trailer(self, movie_name: str):
        """
        Fetch the YouTube trailer link for a movie using TMDb.
        Returns a YouTube URL or None if not found.
        """
        try:
            async with aiohttp.ClientSession() as session:
                search_url = f"{self.base_url}/search/movie"
                search_params = {"api_key": self.api_key, "query": movie_name}
                
                async with session.get(search_url, params=search_params) as search_resp:
                    if search_resp.status != 200:
                        logger.error(f"TMDb search error: {search_resp.status}")
                        return None
                    search_data = await search_resp.json()
                
                if not search_data.get("results"):
                    logger.warning(f"No movie found for '{movie_name}'.")
                    return None
                
                movie_id = search_data["results"][0]["id"]

                videos_url = f"{self.base_url}/movie/{movie_id}/videos"
                videos_params = {"api_key": self.api_key}

                async with session.get(videos_url, params=videos_params) as videos_resp:
                    if videos_resp.status != 200:
                        logger.error(f"TMDb videos error: {videos_resp.status}")
                        return None
                    videos_data = await videos_resp.json()
                
                trailers = [v for v in videos_data.get("results", []) if v.get("site", "").lower() == "youtube" and v.get("type", "").lower() == "trailer"]

                if trailers:
                    trailer = trailers[0]
                    youtube_link = f"https://www.youtube.com/watch?v={trailer['key']}"
                    logger.info(f"🎬 Found trailer: {trailer['name']}")
                    return youtube_link,

                logger.info(f"No YouTube trailers found for '{movie_name}'.")
                return None

        except Exception as e:
            logger.error(f"Error fetching trailer for '{movie_name}': {str(e)}")
            return None 
    
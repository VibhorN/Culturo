"""
Spotify API Integration
Handles music data retrieval for cultural context
"""

import aiohttp
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SpotifyIntegration:
    """Integration with Spotify API for music data"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = 0  # Initialize to 0 instead of None
    
    async def get_access_token(self) -> bool:
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
    
    async def search_playlists(self, country: str, limit: int = 5) -> Optional[List[Dict]]:
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
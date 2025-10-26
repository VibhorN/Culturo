"""
Spotify API Integration
Handles music data retrieval for cultural context via playlist sampling
"""

import aiohttp
import logging
import random
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SpotifyIntegration:
    """Integration with Spotify API for music data"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = 0
    
    async def get_access_token(self) -> bool:
        """Get Spotify access token"""
        try:
            auth_url = "https://accounts.spotify.com/api/token"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
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

    async def get_playlist_tracks(self, playlist_id: str, limit: int = 50) -> List[Dict]:
        """Retrieve tracks from a given playlist"""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
            params = {"limit": limit}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("items", [])
                    else:
                        logger.warning(f"Failed to get tracks for playlist {playlist_id}: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching playlist tracks: {str(e)}")
            return []
    
    async def search_country_songs(self, country: str, limit: int = 3) -> Optional[List[Dict]]:
        """
        Use playlists related to a country to sample songs.
        - Finds up to 3 playlists.
        - Pulls up to `limit` tracks from each.
        - Randomly selects 3 unique songs overall.
        """
        try:
            if not self.access_token or datetime.now().timestamp() >= self.token_expires_at:
                await self.get_access_token()
            
            if not self.access_token:
                return None
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            search_queries = [
                f"{country} top hits",
                f"{country} popular songs",
                f"music from {country}"
            ]
            
            playlists = []
            
            async with aiohttp.ClientSession() as session:
                for query in search_queries:
                    params = {
                        "q": query,
                        "type": "playlist",
                        "limit": limit * 3
                    }
                    async with session.get(
                        "https://api.spotify.com/v1/search",
                        headers=headers,
                        params=params
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            items = data.get("playlists", {}).get("items", [])
                            if items and items[0]:
                                playlists.append(items[0])
                                logger.info(f"Found playlist for '{query}': {items[0]['name']}")
                        else:
                            error_text = await response.text()
                            logger.warning(f"Spotify search error for '{query}': {response.status} - {error_text}")
                    
            
            all_tracks = []
            for playlist in playlists:
                playlist_id = playlist["id"]
                playlist_tracks = await self.get_playlist_tracks(playlist_id)
                
                # Take up to `limit` songs from each playlist
                selected_tracks = random.sample(playlist_tracks, min(limit, len(playlist_tracks)))
                for item in selected_tracks:
                    track = item.get("track")
                    if track:
                        track_info = {
                            "song_name": track["name"],
                            "artist_name": track["artists"][0]["name"] if track.get("artists") else "Unknown Artist",
                            "spotify_url": track["external_urls"]["spotify"],
                        }
                        album_images = track.get("album", {}).get("images", [])
                        if album_images:
                            track_info["image_url"] = album_images[0]["url"]
                        all_tracks.append(track_info)
            
            # Randomly select up to 3 unique songs overall
            random.shuffle(all_tracks)
            return all_tracks[:3]
        
        except Exception as e:
            logger.error(f"Error searching Spotify songs from playlists: {str(e)}")
            return Noness
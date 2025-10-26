import aiohttp
import logging

logger = logging.getLogger(__name__)

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
                    # Check if trailer has a valid key
                    if trailer.get('key'):
                        youtube_link = f"https://www.youtube.com/watch?v={trailer['key']}"
                        logger.info(f"🎬 Found trailer: {trailer['name']}")
                        return youtube_link
                    else:
                        logger.warning(f"Trailer found for '{movie_name}' but no key available")

                logger.info(f"No YouTube trailers found for '{movie_name}'.")
                return None

        except Exception as e:
            logger.error(f"Error fetching trailer for '{movie_name}': {str(e)}")
            return None

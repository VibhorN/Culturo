"""
Reddit API Integration
"""

import aiohttp
import logging

logger = logging.getLogger(__name__)

class RedditIntegration:
    """Integration with Reddit API for slang and cultural insights"""
    
    def __init__(self, client_id, client_secret, user_agent):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
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

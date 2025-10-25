"""
Anthropic Claude Integration
"""

import aiohttp
import json
import logging

logger = logging.getLogger(__name__)

class AnthropicIntegration:
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
                "model": "claude-3-haiku-20240307",
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

"""
Vapi Text-to-Speech Integration
"""

import aiohttp
import logging

logger = logging.getLogger(__name__)

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

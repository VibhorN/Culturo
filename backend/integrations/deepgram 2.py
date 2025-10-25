"""
Deepgram Speech-to-Text Integration
"""

import aiohttp
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

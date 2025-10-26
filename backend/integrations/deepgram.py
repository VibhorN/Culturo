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
    
    async def transcribe_audio(self, audio_data, language="en-US", content_type="audio/webm"):
        """Transcribe audio using Deepgram API"""
        try:
            headers = {
                "Authorization": f"Token {self.api_key}"
            }
            
            params = {
                "model": "nova-2",
                "punctuate": "true",
                "diarize": "false"
            }
            
            # Only add language parameter if it's not 'auto'
            if language and language != 'auto':
                params["language"] = language
            
            # Create multipart form data
            data = aiohttp.FormData()
            data.add_field('audio', audio_data, filename='audio.webm', content_type=content_type)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/listen",
                    headers=headers,
                    params=params,
                    data=data
                ) as response:
                    response_text = await response.text()
                    logger.info(f"Deepgram response status: {response.status}")
                    logger.info(f"Deepgram response body: {response_text[:200]}...")
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Full Deepgram response: {result}")
                        
                        # Check if we have results and transcript
                        if (result.get("results") and 
                            result["results"].get("channels") and 
                            len(result["results"]["channels"]) > 0 and
                            result["results"]["channels"][0].get("alternatives") and
                            len(result["results"]["channels"][0]["alternatives"]) > 0):
                            
                            transcript = result["results"]["channels"][0]["alternatives"][0].get("transcript", "")
                            confidence = result["results"]["channels"][0]["alternatives"][0].get("confidence", 0)
                            
                            if transcript.strip():
                                return {
                                    "transcript": transcript,
                                    "confidence": confidence,
                                    "language": language
                                }
                            else:
                                logger.warning("Deepgram returned empty transcript")
                                return {
                                    "transcript": "",
                                    "confidence": 0,
                                    "language": language,
                                    "error": "No speech detected or transcript is empty"
                                }
                        else:
                            logger.warning("Deepgram response missing expected structure")
                            return {
                                "transcript": "",
                                "confidence": 0,
                                "language": language,
                                "error": "Invalid response structure from Deepgram"
                            }
                    else:
                        logger.error(f"Deepgram API error: {response.status} - {response_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error in Deepgram transcription: {str(e)}")
            return None

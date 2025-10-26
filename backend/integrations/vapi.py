"""
Vapi Text-to-Speech Integration
"""

import aiohttp
import logging

logger = logging.getLogger(__name__)

class VapiIntegration:
    """Integration with VAPI for voice AI conversations"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.vapi.ai"
    
    async def create_assistant(self, name="Cultural Assistant", system_prompt="You are a friendly cultural assistant."):
        """Create a VAPI assistant for voice conversations"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            assistant_data = {
                "name": name,
                "model": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        }
                    ]
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "21m00Tcm4TlvDq8ikWAM"  # Default voice
                },
                "firstMessage": "Hello! I'm your cultural assistant. How can I help you explore different cultures today?",
                "maxDurationSeconds": 300,
                "endCallMessage": "Thank you for exploring cultures with me! Have a great day!",
                "endCallPhrases": ["goodbye", "bye", "see you later", "thanks"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/assistant",
                    headers=headers,
                    json=assistant_data
                ) as response:
                    if response.status in [200, 201]:  # Accept both 200 and 201
                        result = await response.json()
                        logger.info(f"Created VAPI assistant: {result.get('id')}")
                        return result
                    else:
                        response_text = await response.text()
                        logger.error(f"VAPI assistant creation failed: {response.status} - {response_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error creating VAPI assistant: {str(e)}")
            return None
    
    async def create_web_call(self, assistant_id, customer_number="+15551234567"):
        """Create a web-based voice call using VAPI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            call_data = {
                "assistantId": assistant_id,
                "customer": {
                    "number": customer_number
                },
                "type": "outboundPhoneCall"  # Use valid call type
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/call",
                    headers=headers,
                    json=call_data
                ) as response:
                    if response.status in [200, 201]:  # Accept both 200 and 201
                        result = await response.json()
                        logger.info(f"Created VAPI web call: {result.get('id')}")
                        return result
                    else:
                        response_text = await response.text()
                        logger.error(f"VAPI call creation failed: {response.status} - {response_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error creating VAPI call: {str(e)}")
            return None
    
    async def synthesize_speech(self, text, voice="alloy", language="en"):
        """Create a voice conversation using VAPI"""
        try:
            # For now, let's create an assistant and return the assistant info
            # This allows the frontend to handle the voice interaction
            assistant = await self.create_assistant(
                name="Cultural Voice Assistant",
                system_prompt=f"You are a friendly cultural assistant. Respond to this: {text}"
            )
            
            if not assistant:
                return None
            
            assistant_id = assistant.get("id")
            
            logger.info(f"VAPI assistant created: {assistant_id}")
            
            return {
                "audio_url": None,  # VAPI handles audio streaming
                "duration": None,
                "language": language,
                "vapi_call": True,
                "assistant_id": assistant_id,
                "message": "Voice assistant created with VAPI",
                "assistant_url": f"https://dashboard.vapi.ai/assistant/{assistant_id}",  # Link to assistant dashboard
                "text": text  # Include the original text for fallback
            }
            
        except Exception as e:
            logger.error(f"Error in VAPI voice conversation: {str(e)}")
            return None

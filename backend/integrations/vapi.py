"""
Vapi Text-to-Speech Integration
"""

import aiohttp
import logging
import os

logger = logging.getLogger(__name__)

class VapiIntegration:
    """Integration with VAPI for voice AI conversations"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.vapi.ai"
        
        # Language-specific voice configurations for natural accents
        self.voice_configs = {
            "en": {
                "provider": "11labs",
                "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Natural American English
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "es": {
                "provider": "11labs", 
                "voiceId": "AZnzlk1XvdvUeBnXmlld",  # Domi - Natural Spanish accent
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "fr": {
                "provider": "11labs",
                "voiceId": "EXAVITQu4vr4xnSDxMaL",  # Bella - Natural French accent
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "de": {
                "provider": "11labs",
                "voiceId": "ErXwobaYiN019PkySvjV",  # Antoni - Natural German accent
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "it": {
                "provider": "11labs",
                "voiceId": "VR6AewLTigWG4xSOukaG",  # Josh - Natural Italian accent
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "pt": {
                "provider": "11labs",
                "voiceId": "AZnzlk1XvdvUeBnXmlld",  # Domi - Good for Portuguese
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "ja": {
                "provider": "11labs",
                "voiceId": "VR6AewLTigWG4xSOukaG",  # Josh - Good for Japanese
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "ko": {
                "provider": "11labs",
                "voiceId": "VR6AewLTigWG4xSOukaG",  # Josh - Good for Korean
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "zh": {
                "provider": "11labs",
                "voiceId": "VR6AewLTigWG4xSOukaG",  # Josh - Good for Chinese
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        # Language-specific greetings and responses
        self.language_greetings = {
            "en": "Hello! I'm your cultural assistant. How can I help you explore different cultures today?",
            "es": "¡Hola! Soy tu asistente cultural. ¿Cómo puedo ayudarte a explorar diferentes culturas hoy?",
            "fr": "Bonjour! Je suis votre assistant culturel. Comment puis-je vous aider à explorer différentes cultures aujourd'hui?",
            "de": "Hallo! Ich bin Ihr kultureller Assistent. Wie kann ich Ihnen heute helfen, verschiedene Kulturen zu erkunden?",
            "it": "Ciao! Sono il tuo assistente culturale. Come posso aiutarti a esplorare diverse culture oggi?",
            "pt": "Olá! Sou seu assistente cultural. Como posso ajudá-lo a explorar diferentes culturas hoje?",
            "ja": "こんにちは！私はあなたの文化的アシスタントです。今日はどのように異なる文化を探索するのをお手伝いできますか？",
            "ko": "안녕하세요! 저는 당신의 문화 어시스턴트입니다. 오늘 어떻게 다른 문화를 탐험하는 것을 도와드릴까요?",
            "zh": "你好！我是你的文化助手。今天我能如何帮助你探索不同的文化？"
        }
        
        self.language_endings = {
            "en": "Thank you for exploring cultures with me! Have a great day!",
            "es": "¡Gracias por explorar culturas conmigo! ¡Que tengas un gran día!",
            "fr": "Merci d'avoir exploré les cultures avec moi! Passez une excellente journée!",
            "de": "Vielen Dank, dass Sie Kulturen mit mir erkundet haben! Haben Sie einen schönen Tag!",
            "it": "Grazie per aver esplorato le culture con me! Buona giornata!",
            "pt": "Obrigado por explorar culturas comigo! Tenha um ótimo dia!",
            "ja": "私と一緒に文化を探索していただき、ありがとうございました！良い一日を！",
            "ko": "저와 함께 문화를 탐험해 주셔서 감사합니다! 좋은 하루 되세요!",
            "zh": "谢谢你和我一起探索文化！祝你今天愉快！"
        }
    
    def _get_end_phrases(self, language):
        """Get language-specific end call phrases"""
        end_phrases = {
            "en": ["goodbye", "bye", "see you later", "thanks", "thank you", "that's all"],
            "es": ["adiós", "hasta luego", "gracias", "hasta la vista", "nos vemos"],
            "fr": ["au revoir", "à bientôt", "merci", "salut", "à plus"],
            "de": ["auf wiedersehen", "tschüss", "danke", "bis später", "tschau"],
            "it": ["arrivederci", "ciao", "grazie", "a presto", "ci vediamo"],
            "pt": ["tchau", "até logo", "obrigado", "até mais", "nos vemos"],
            "ja": ["さようなら", "ありがとう", "またね", "お疲れ様"],
            "ko": ["안녕히 가세요", "감사합니다", "다음에 봐요", "수고하세요"],
            "zh": ["再见", "谢谢", "下次见", "辛苦了"]
        }
        return end_phrases.get(language, end_phrases["en"])
    
    async def _detect_language_with_llm(self, text):
        """Use LLM to detect language from text"""
        try:
            # Get Anthropic API key
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            if not anthropic_api_key:
                logger.warning("No Anthropic API key found, using heuristic language detection")
                return self._detect_language_heuristic(text)
            
            headers = {
                "x-api-key": anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            prompt = f"""Detect the language of this text and respond with only the ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh').

Text: "{text}"

Language code:"""
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 10,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        language_code = result["content"][0]["text"].strip().lower()
                        
                        # Validate the language code
                        valid_codes = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh']
                        if language_code in valid_codes:
                            logger.info(f"LLM detected language: {language_code}")
                            return language_code
                        else:
                            logger.warning(f"Invalid language code from LLM: {language_code}, using heuristic")
                            return self._detect_language_heuristic(text)
                    else:
                        logger.warning(f"LLM language detection failed: {response.status}, using heuristic")
                        return self._detect_language_heuristic(text)
                        
        except Exception as e:
            logger.warning(f"LLM language detection error: {str(e)}, using heuristic")
            return self._detect_language_heuristic(text)
    
    def _detect_language_heuristic(self, text):
        """Fallback heuristic language detection"""
        try:
            # Simple heuristic for common cases to avoid unnecessary API calls
            if len(text.strip()) < 3:
                return "en"
            
            # Check for obvious non-Latin scripts first
            if any('\u3040' <= char <= '\u309F' for char in text):  # Hiragana
                return "ja"
            elif any('\u30A0' <= char <= '\u30FF' for char in text):  # Katakana
                return "ja"
            elif any('\u4E00' <= char <= '\u9FFF' for char in text):  # CJK Unified Ideographs
                return "zh"
            elif any('\uAC00' <= char <= '\uD7AF' for char in text):  # Hangul
                return "ko"
            
            # For Latin-based scripts, use ordered detection (most specific first)
            text_lower = text.lower()
            
            # Check for specific language indicators in order of specificity
            
            # Spanish indicators (most specific first)
            spanish_specific = ['ñ', '¿', '¡', 'español', 'gracias', 'hola', 'adiós', 'cómo', 'qué', 'dónde', 'cuándo']
            if any(indicator in text_lower or indicator in text for indicator in spanish_specific):
                return "es"
            
            # French indicators
            french_specific = ['ç', 'français', 'bonjour', 'merci', 's\'il vous plaît', 'au revoir', 'où', 'quand']
            if any(indicator in text_lower or indicator in text for indicator in french_specific):
                return "fr"
            
            # German indicators
            german_specific = ['ß', 'ä', 'ö', 'ü', 'deutsch', 'hallo', 'danke', 'bitte', 'auf wiedersehen']
            if any(indicator in text_lower or indicator in text for indicator in german_specific):
                return "de"
            
            # Italian indicators
            italian_specific = ['italiano', 'ciao', 'grazie', 'prego', 'arrivederci', 'come', 'dove', 'quando']
            if any(indicator in text_lower for indicator in italian_specific):
                return "it"
            
            # Portuguese indicators
            portuguese_specific = ['português', 'olá', 'obrigado', 'tchau', 'sim', 'não', 'como', 'onde', 'quando']
            if any(indicator in text_lower for indicator in portuguese_specific):
                return "pt"
            
            # English indicators (common English words)
            english_specific = ['english', 'hello', 'thank you', 'please', 'goodbye', 'culture', 'country']
            if any(indicator in text_lower for indicator in english_specific):
                return "en"
            
            # Default to English for ambiguous cases
            return "en"
            
        except Exception as e:
            logger.warning(f"Language detection failed, defaulting to English: {str(e)}")
            return "en"
    
    async def create_assistant(self, name="Cultural Assistant", system_prompt="You are a friendly cultural assistant.", language="en"):
        """Create a VAPI assistant for voice conversations with language-specific voice"""
        try:
            logger.info(f"Creating VAPI assistant: name='{name}', language='{language}'")
            
            # Validate API key
            if not self.api_key:
                logger.error("VAPI API key not provided")
                return None
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Get language-specific voice configuration
            voice_config = self.voice_configs.get(language, self.voice_configs["en"])
            greeting = self.language_greetings.get(language, self.language_greetings["en"])
            ending = self.language_endings.get(language, self.language_endings["en"])
            
            logger.info(f"Using voice config for {language}: {voice_config['voiceId']}")
            
            # Enhanced voice configuration for more natural speech
            voice_settings = {
                "provider": voice_config["provider"],
                "voiceId": voice_config["voiceId"],
                "stability": voice_config["stability"],
                "similarityBoost": voice_config["similarity_boost"],
                "style": voice_config["style"],
                "useSpeakerBoost": voice_config["use_speaker_boost"]
            }
            
            # Language-specific system prompt
            language_system_prompt = f"You are a friendly cultural assistant speaking {language.upper()}. {system_prompt}"
            
            assistant_data = {
                "name": f"{name} ({language.upper()})",
                "model": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": language_system_prompt
                        }
                    ],
                    "temperature": 0.7,  # More natural responses
                    "maxTokens": 150
                },
                "voice": voice_settings,
                "firstMessage": greeting,
                "maxDurationSeconds": 300,
                "endCallMessage": ending,
                "endCallPhrases": self._get_end_phrases(language),
                "backgroundSound": "off",  # Clean audio
                "silenceTimeoutSeconds": 10,  # Must be at least 10
                "responseDelaySeconds": 0.8,  # Natural pause
                "recordingEnabled": False,
                "endCallFunctionEnabled": False,
                "fillersEnabled": True,  # Natural speech patterns
                "backchannelingEnabled": True,  # Natural conversation flow
                "voicemailDetectionEnabled": False
            }
            
            logger.info(f"Sending VAPI assistant creation request for {language}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/assistant",
                    headers=headers,
                    json=assistant_data,
                    timeout=30
                ) as response:
                    response_text = await response.text()
                    
                    if response.status in [200, 201]:
                        try:
                            result = await response.json()
                            assistant_id = result.get('id')
                            if assistant_id:
                                logger.info(f"Created VAPI assistant ({language}): {assistant_id}")
                                return result
                            else:
                                logger.error(f"VAPI assistant created but no ID in response: {result}")
                                return None
                        except Exception as json_error:
                            logger.error(f"Failed to parse VAPI response JSON: {str(json_error)}")
                            logger.error(f"Response text: {response_text}")
                            return None
                    else:
                        logger.error(f"VAPI assistant creation failed: {response.status} - {response_text}")
                        return None
                        
        except aiohttp.ClientError as client_error:
            logger.error(f"VAPI client error: {str(client_error)}")
            return None
        except Exception as e:
            logger.error(f"Error creating VAPI assistant: {str(e)}", exc_info=True)
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
        """Create a voice conversation using VAPI with language-specific voice"""
        try:
            logger.info(f"Starting VAPI synthesis: text='{text[:50]}...', language='{language}'")
            
            # Validate inputs
            if not text or not text.strip():
                logger.error("Empty text provided to VAPI synthesis")
                return None
            
            # Use LLM to detect language if not provided or auto
            if language == "auto" or not language:
                logger.info("Auto-detecting language using LLM")
                detected_language = await self._detect_language_with_llm(text)
            else:
                detected_language = language
            
            logger.info(f"Using language: {detected_language} for text: {text[:50]}...")
            
            # Create assistant with language-specific voice and settings
            logger.info(f"Creating VAPI assistant for language: {detected_language}")
            assistant = await self.create_assistant(
                name="Cultural Voice Assistant",
                system_prompt=f"You are a friendly cultural assistant. Respond naturally to this: {text}",
                language=detected_language
            )
            
            if not assistant:
                logger.error("Failed to create VAPI assistant")
                return None
            
            assistant_id = assistant.get("id")
            if not assistant_id:
                logger.error("VAPI assistant created but no ID returned")
                return None
            
            logger.info(f"VAPI assistant created successfully ({detected_language}): {assistant_id}")
            
            return {
                "audio_url": None,  # VAPI handles audio streaming
                "duration": None,
                "language": detected_language,
                "vapi_call": True,
                "assistant_id": assistant_id,
                "message": f"Voice assistant created with VAPI ({detected_language.upper()})",
                "assistant_url": f"https://dashboard.vapi.ai/assistant/{assistant_id}",
                "text": text,
                "voice_info": {
                    "language": detected_language,
                    "voice_id": self.voice_configs.get(detected_language, self.voice_configs["en"])["voiceId"],
                    "provider": "11labs"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in VAPI voice conversation: {str(e)}", exc_info=True)
            return None

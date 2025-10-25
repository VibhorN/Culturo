"""
Translation Agent
Handles translation between languages with cultural context
"""

import json
import logging
import aiohttp
import time
from typing import Dict
from .base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

# Import logging system
try:
    from logging_system import log_api_call
except ImportError:
    def log_api_call(*args, **kwargs):
        pass


class TranslationAgent(BaseAgent):
    """
    Handles translation between languages with cultural context
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("Translation", anthropic_api_key)
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Translates text with cultural context
        """
        try:
            text = input_data.get("text", "")
            source_language = input_data.get("source_language", "en")
            target_language = input_data.get("target_language", "en")
            context = input_data.get("context", {})
            
            logger.info(f"[Translation] {source_language} -> {target_language}: '{text}'")
            
            translation = await self._translate_with_context(
                text, 
                source_language, 
                target_language,
                context
            )
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data=translation,
                confidence=translation.get("confidence", 0.8),
                reasoning=translation.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"[Translation] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _translate_with_context(self, text: str, source_lang: str, target_lang: str, context: Dict) -> Dict:
        """Use Claude via Anthropic API to translate with cultural context"""
        try:
            prompt = f"""
            You are a professional translator with deep cultural knowledge.
            Translate this text considering cultural context and nuances.
            
            Text: "{text}"
            Source Language: {source_lang}
            Target Language: {target_lang}
            Context: {json.dumps(context)}
            
            Provide:
            1. Direct translation
            2. Cultural adaptation (if needed)
            3. Alternative translations
            4. Cultural notes
            5. Confidence level
            
            Respond in JSON:
            {{
                "direct_translation": "...",
                "cultural_adaptation": "...",
                "alternatives": [
                    {{"translation": "...", "context": "...", "formality": "formal/casual"}}
                ],
                "cultural_notes": ["note1", "note2"],
                "pronunciation_guide": "...",
                "confidence": 0.9,
                "reasoning": "..."
            }}
            """
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 800,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    execution_time = time.time() - start_time
                    
                    # Log API call
                    log_api_call(
                        service="anthropic",
                        endpoint="/v1/messages",
                        method="POST",
                        request_data=data,
                        response_data={"status": response.status, "content": "..."},
                        status_code=response.status,
                        execution_time=execution_time
                    )
                    
                    if response.status == 200:
                        result = await response.json()
                        translation_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = translation_text.find('{')
            end_idx = translation_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(translation_text[start_idx:end_idx])
                    
        except Exception as e:
            logger.error(f"[Translation] Error: {str(e)}")
        
        return {
            "direct_translation": text,
            "cultural_adaptation": text,
            "alternatives": [],
            "cultural_notes": [],
            "pronunciation_guide": "",
            "confidence": 0.3,
            "reasoning": "Unable to translate"
        }

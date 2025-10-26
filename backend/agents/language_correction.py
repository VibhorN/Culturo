"""
Language Correction Agent
Analyzes user's language input for grammar mistakes, pronunciation issues, and better phrasing
"""

import json
import logging
import aiohttp
from typing import Dict
from .base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


class LanguageCorrectionAgent(BaseAgent):
    """
    Analyzes user's language input for:
    - Grammar mistakes
    - Pronunciation issues
    - Better phrasing suggestions
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("LanguageCorrection", anthropic_api_key)
    
    async def process(self, input_data: Dict) -> AgentResponse:
        """
        Analyzes language input and provides corrections
        """
        try:
            text = input_data.get("text", "")
            target_language = input_data.get("target_language", "en")
            user_native_language = input_data.get("native_language", "en")
            audio_confidence = input_data.get("audio_confidence", 1.0)
            
            logger.info(f"[LanguageCorrection] Analyzing: '{text}'")
            
            corrections = await self._analyze_language(
                text, 
                target_language, 
                user_native_language,
                audio_confidence
            )
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data=corrections,
                confidence=corrections.get("confidence", 0.8),
                reasoning=corrections.get("explanation", "")
            )
            
        except Exception as e:
            logger.error(f"[LanguageCorrection] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _analyze_language(self, text: str, target_lang: str, native_lang: str, audio_conf: float) -> Dict:
        """Use Claude via Anthropic API to analyze language and provide corrections"""
        try:
            prompt = f"""
            You are a language correction expert. Analyze this text for mistakes.
            
            Text: "{text}"
            Target Language: {target_lang}
            User's Native Language: {native_lang}
            Audio Confidence: {audio_conf} (lower means possibly misheard)
            
            Provide:
            1. Grammar corrections (if any)
            2. Pronunciation tips (if audio confidence is low)
            3. Better phrasing suggestions
            4. Cultural appropriateness
            5. Confidence in your corrections (0-1)
            
            Respond in JSON:
            {{
                "has_errors": true/false,
                "grammar_corrections": [
                    {{"original": "...", "corrected": "...", "explanation": "..."}}
                ],
                "pronunciation_tips": ["tip1", "tip2"],
                "better_phrases": [
                    {{"original": "...", "improved": "...", "why": "..."}}
                ],
                "cultural_notes": ["note1", "note2"],
                "overall_quality": "excellent/good/needs_work",
                "confidence": 0.9,
                "explanation": "..."
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
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        corrections_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = corrections_text.find('{')
            end_idx = corrections_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(corrections_text[start_idx:end_idx])
                    
        except Exception as e:
            logger.error(f"[LanguageCorrection] Error: {str(e)}")
        
        return {
            "has_errors": False,
            "grammar_corrections": [],
            "pronunciation_tips": [],
            "better_phrases": [],
            "cultural_notes": [],
            "overall_quality": "unknown",
            "confidence": 0.3,
            "explanation": "Unable to analyze"
        }

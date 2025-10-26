"""
Cultural Context Agent
Provides cultural insights and context for different countries
"""

import json
import logging
import aiohttp
from typing import Dict
from .base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


class CulturalContextAgent(BaseAgent):
    """
    Provides cultural insights and context for different countries
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("CulturalContext", anthropic_api_key)
    
    async def process(self, input_data: Dict) -> AgentResponse:
        """
        Analyzes cultural context and provides insights
        """
        try:
            country = input_data.get("country", "unknown")
            intent = input_data.get("intent", "general")
            data_sources = input_data.get("data_sources", [])
            
            logger.info(f"[CulturalContext] Analyzing {country} - {intent}")
            
            insights = await self._analyze_culture(country, intent, data_sources)
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data=insights,
                confidence=insights.get("confidence", 0.8),
                reasoning=insights.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"[CulturalContext] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _analyze_culture(self, country: str, intent: str, data_sources: list) -> Dict:
        """Use Claude via Anthropic API to analyze cultural context"""
        try:
            prompt = f"""
            You are a cultural expert. Provide insights about {country} based on the user's intent.
            
            Country: {country}
            Intent: {intent}
            Data Sources Available: {data_sources}
            
            Provide:
            1. Key cultural insights relevant to the intent
            2. Important customs and traditions
            3. Language nuances and expressions
            4. Social norms and etiquette
            5. Common misconceptions to avoid
            6. Practical tips for travelers/learners
            
            Respond in JSON:
            {{
                "cultural_insights": [
                    {{"category": "...", "insight": "...", "importance": "high/medium/low"}}
                ],
                "customs": ["custom1", "custom2"],
                "language_nuances": ["nuance1", "nuance2"],
                "etiquette": ["rule1", "rule2"],
                "misconceptions": ["myth1", "myth2"],
                "practical_tips": ["tip1", "tip2"],
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
                "max_tokens": 1000,
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
                        insights_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = insights_text.find('{')
            end_idx = insights_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(insights_text[start_idx:end_idx])
                    
        except Exception as e:
            logger.error(f"[CulturalContext] Error: {str(e)}")
        
        return {
            "cultural_insights": [],
            "customs": [],
            "language_nuances": [],
            "etiquette": [],
            "misconceptions": [],
            "practical_tips": [],
            "confidence": 0.3,
            "reasoning": "Unable to analyze"
        }

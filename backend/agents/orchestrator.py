"""
Orchestrator Agent
Main coordinator that analyzes user input and creates execution plans
"""

import json
import logging
import aiohttp
from typing import Dict
from .base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Main coordinator agent that receives user input and decides:
    - Which data sources to query
    - Which agents to activate
    - The order of agent execution
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("Orchestrator", anthropic_api_key)
    
    async def process(self, input_data: Dict) -> AgentResponse:
        """
        Analyzes user input and creates execution plan
        """
        try:
            user_query = input_data.get("query", "")
            user_language = input_data.get("language", "en")
            context = input_data.get("context", {})
            
            logger.info(f"[Orchestrator] Processing query: {user_query}")
            
            # Use Claude to analyze intent and create plan
            plan = await self._analyze_intent(user_query, user_language, context)
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data=plan,
                confidence=plan.get("confidence", 0.8),
                reasoning=plan.get("reasoning", ""),
                next_actions=plan.get("agents_to_activate", [])
            )
            
        except Exception as e:
            logger.error(f"[Orchestrator] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _analyze_intent(self, query: str, language: str, context: Dict) -> Dict:
        """Use Claude via Anthropic API to analyze user intent and create execution plan"""
        try:
            prompt = f"""
            You are the Orchestrator Agent for WorldWise, a cultural immersion AI assistant.
            Analyze this user query and determine what actions to take.
            
            User Query: "{query}"
            User Language: {language}
            Context: {json.dumps(context)}
            
            Determine:
            1. What is the user's intent? (learn_language, cultural_info, pronunciation_help, travel_advice, etc.)
            2. What country/culture are they interested in?
            3. Which data sources should be queried? (government, music, food, slang, news, etc.)
            4. Which agents should be activated? (language_correction, cultural_context, translation, etc.)
            5. Does this require real-time voice processing?
            6. Confidence level (0-1)
            
            Respond in JSON format:
            {{
                "intent": "intent_type",
                "target_country": "country_name",
                "data_sources": ["source1", "source2"],
                "agents_to_activate": ["agent1", "agent2"],
                "requires_voice": true/false,
                "confidence": 0.9,
                "reasoning": "explanation"
            }}
            """
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 500,
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
                        plan_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            # Extract JSON from response
            start_idx = plan_text.find('{')
            end_idx = plan_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                plan = json.loads(plan_text[start_idx:end_idx])
                logger.info(f"[Orchestrator] Created plan: {plan}")
                return plan
                    
        except Exception as e:
            logger.error(f"[Orchestrator] Error analyzing intent: {str(e)}")
        
        # Fallback plan
        return {
            "intent": "cultural_info",
            "target_country": "unknown",
            "data_sources": ["government", "music", "food"],
            "agents_to_activate": ["cultural_context", "conversation"],
            "requires_voice": False,
            "confidence": 0.3,
            "reasoning": "Fallback plan due to error"
        }

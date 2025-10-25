"""
Conversation Agent
Generates natural, engaging responses for user interactions
"""

import json
import logging
import aiohttp
from typing import Dict
from .base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


class ConversationAgent(BaseAgent):
    """
    Generates natural, engaging responses for user interactions
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("Conversation", anthropic_api_key)
    
    async def process(self, input_data: Dict) -> AgentResponse:
        """
        Generates conversational response
        """
        try:
            user_query = input_data.get("query", "")
            context = input_data.get("context", {})
            cultural_data = input_data.get("cultural_data", {})
            language_corrections = input_data.get("language_corrections", {})
            
            logger.info(f"[Conversation] Generating response to: '{user_query}'")
            
            response = await self._generate_response(
                user_query, 
                context, 
                cultural_data,
                language_corrections
            )
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data=response,
                confidence=response.get("confidence", 0.8),
                reasoning=response.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"[Conversation] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _generate_response(self, query: str, context: Dict, cultural_data: Dict, corrections: Dict) -> Dict:
        """Use Claude via Anthropic API to generate conversational response"""
        try:
            prompt = f"""
            You are WorldWise, a friendly cultural immersion AI assistant.
            Generate a natural, engaging response to the user's query.
            
            User Query: "{query}"
            Context: {json.dumps(context)}
            Cultural Data: {json.dumps(cultural_data)}
            Language Corrections: {json.dumps(corrections)}
            
            Guidelines:
            - Be warm, helpful, and culturally sensitive
            - Incorporate cultural insights naturally
            - Address any language corrections gently
            - Ask follow-up questions to deepen engagement
            - Keep responses conversational, not academic
            
            Respond in JSON:
            {{
                "response": "Your natural response here...",
                "follow_up_questions": ["question1", "question2"],
                "cultural_highlights": ["highlight1", "highlight2"],
                "learning_tips": ["tip1", "tip2"],
                "tone": "friendly/encouraging/curious",
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
                "model": "claude-3-sonnet-20240229",
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
                        response_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(response_text[start_idx:end_idx])
                    
        except Exception as e:
            logger.error(f"[Conversation] Error: {str(e)}")
        
        return {
            "response": "I'd be happy to help you learn more about different cultures! Could you tell me which country or culture you're most interested in?",
            "follow_up_questions": ["What sparked your interest in this culture?", "Are you planning to visit or just curious?"],
            "cultural_highlights": [],
            "learning_tips": [],
            "tone": "friendly",
            "confidence": 0.3,
            "reasoning": "Fallback response"
        }

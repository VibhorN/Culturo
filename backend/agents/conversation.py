"""
Conversation Agent
Generates natural, engaging responses for user interactions
"""

import json
import logging
import aiohttp
import time
from typing import Dict
from core.base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

# Import logging system
try:
    from utils.logging import log_api_call
except ImportError:
    def log_api_call(*args, **kwargs):
        pass


class ConversationAgent(BaseAgent):
    """
    Generates natural, engaging responses for user interactions
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("Conversation", anthropic_api_key)
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Generates conversational response
        """
        try:
            user_query = input_data.get("query", "")
            context = input_data.get("context", {})
            retrieved_data = input_data.get("retrieved_data", {})
            language_corrections = input_data.get("language_corrections", {})
            
            logger.info(f"[Conversation] Generating response to: '{user_query}'")
            
            response = await self._generate_response(
                user_query, 
                context, 
                retrieved_data,
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
    
    async def _generate_response(self, query: str, context: Dict, retrieved_data: Dict, corrections: Dict) -> Dict:
        """Use Claude via Anthropic API to generate conversational response"""
        try:
            has_retrieved_data = len(retrieved_data) > 0 and retrieved_data != {}
            
            prompt = f"""
            You are WorldWise, a friendly cultural immersion AI assistant.
            Generate a natural, engaging response to the user's query.
            
            User Query: "{query}"
            Context: {json.dumps(context)}
            Has Retrieved Data: {has_retrieved_data}
            Retrieved Data: {json.dumps(retrieved_data) if has_retrieved_data else "No retrieved data available"}
            Language Corrections: {json.dumps(corrections)}
            
            Guidelines:
            - Be warm, helpful, and culturally sensitive
            - For simple conversational queries (like "Who are you?", "What can you do?"), give a direct, friendly response about WorldWise
            - For cultural queries, incorporate retrieved data naturally and show enthusiasm about the culture
            - For interest statements (like "I'm interested in Japan"), respond enthusiastically and provide engaging cultural information
            - Address any language corrections gently
            - Ask follow-up questions to deepen engagement
            - Keep responses conversational, not academic
            - If clarification is needed, ask specific questions about what they want to know
            
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
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1000,
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

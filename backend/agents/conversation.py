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
            retrieved_data = input_data.get("retrieved_data", {})
            language_corrections = input_data.get("language_corrections", {})
            has_retrieved_data = input_data.get("has_retrieved_data", False)
            
            logger.info(f"[Conversation] Generating response to: '{user_query}'")
            logger.info(f"[Conversation] Has retrieved data: {has_retrieved_data}")
            if retrieved_data:
                logger.info(f"[Conversation] Retrieved data keys: {list(retrieved_data.keys())}")
            
            response = await self._generate_response(
                user_query, 
                context, 
                retrieved_data,
                language_corrections,
                has_retrieved_data
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
    
    async def _generate_response(self, query: str, context: Dict, retrieved_data: Dict, corrections: Dict, has_retrieved_data: bool) -> Dict:
        """Use Claude via Anthropic API to generate conversational response"""
        try:
            # Format retrieved data for better presentation
            data_summary = ""
            if has_retrieved_data and retrieved_data:
                data_summary = "\n\nRETRIEVED DATA TO USE IN RESPONSE:\n"
                for source, data in retrieved_data.items():
                    if source != "_retrieval_log" and data:
                        data_summary += f"\n{source.upper()}:\n"
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if isinstance(value, list) and len(value) > 0:
                                    data_summary += f"  {key}: {value[:3]}{'...' if len(value) > 3 else ''}\n"
                                elif isinstance(value, str) and len(value) > 0:
                                    data_summary += f"  {key}: {value[:100]}{'...' if len(value) > 100 else ''}\n"
                                elif value:
                                    data_summary += f"  {key}: {value}\n"
                        elif isinstance(data, list) and len(data) > 0:
                            data_summary += f"  Items: {data[:3]}{'...' if len(data) > 3 else ''}\n"
                        elif data:
                            data_summary += f"  Data: {str(data)[:100]}{'...' if len(str(data)) > 100 else ''}\n"
            
            prompt = f"""
            You are WorldWise, a friendly cultural immersion AI assistant.
            Generate a natural, engaging response to the user's query.
            
            User Query: "{query}"
            Context: {json.dumps(context)}
            Has Retrieved Data: {has_retrieved_data}
            Language Corrections: {json.dumps(corrections)}
            {data_summary}
            
            Guidelines:
            - Be warm, helpful, and culturally sensitive
            - Keep responses SHORT and CONCISE (2-3 sentences maximum for voice)
            - For simple conversational queries (like "Who are you?", "What can you do?"), give a direct, friendly response about WorldWise
            - For cultural queries, ALWAYS use the retrieved data above to provide specific, accurate information
            - If retrieved data is available, prioritize it over generic knowledge
            - For restaurant/food recommendations, use specific names and details from the retrieved data
            - Address any language corrections gently
            - Ask ONE follow-up question to deepen engagement
            - Keep responses conversational, not academic
            - If clarification is needed, ask specific questions about what they want to know
            - Prioritize the most interesting cultural insights from the retrieved data
            
            Respond in JSON:
            {{
                "response": "Your natural response here...",
                "follow_up_questions": ["question1"],
                "cultural_highlights": ["highlight1", "highlight2"],
                "learning_tips": ["tip1", "tip2"],
                "tone": "friendly/encouraging/curious",
                "confidence": 0.9,
                "reasoning": "Detailed explanation of how you processed the query, what retrieved data you used, and why you chose this response approach",
                "thinking_process": [
                    "Step 1: Analyzed user intent",
                    "Step 2: Identified relevant retrieved data",
                    "Step 3: Selected key insights to highlight",
                    "Step 4: Crafted concise response using specific data"
                ]
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
            "reasoning": "Fallback response due to API error",
            "thinking_process": [
                "Step 1: Detected API error in response generation",
                "Step 2: Using fallback response to maintain conversation flow",
                "Step 3: Asking open-ended question to engage user",
                "Step 4: Providing helpful follow-up questions"
            ]
        }

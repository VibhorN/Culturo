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
            
            CONVERSATION CONTEXT:
            - Last country discussed: {context.get('last_country', 'None')}
            - Recent conversation history: {context.get('conversation_history', [])}
            
            IMPORTANT: If the user asks a follow-up question without specifying a country (like "what are some current events"), 
            and there was a previous country discussed, assume they want information about that same country.
            
            CRITICAL: For vague queries like "tell me about Japan", "what about Japan", "Japan info", "what can you say about Japan", you MUST set needs_clarification: true and ask what specific aspect they want to know about. DO NOT retrieve data for vague queries.
            
            Examples of VAGUE queries that need clarification:
            - "tell me about Japan" → needs_clarification: true
            - "what can you say about Japan" → needs_clarification: true
            - "Japan info" → needs_clarification: true
            - "what about Japan" → needs_clarification: true
            
            Examples of SPECIFIC queries that can proceed:
            - "places to eat in Japan" → use restaurants API
            - "song recommendations for Japan" → use music API  
            - "news about Japan" → use news API
            - "historical sites in Japan" → use landmarks API
            
            Available data sources and their purposes:
            - news: Current cultural news and events
            - music: Song recommendations and playlists
            - landmarks: Historical sites and monuments
            - restaurants: Places to eat and food recommendations
            - destinations: Tourist attractions and places to visit
            - food: Traditional cuisine and dishes
            - movies: Film recommendations
            - government: Political and administrative information
            - festivals: Cultural celebrations and events
            
            Available agents:
            - language_correction: For correcting language mistakes
            - cultural_context: For providing cultural context and information
            - translation: For translating text
            - data_retrieval: For retrieving data from external APIs (use this when data sources are needed)
            - conversation: For generating natural responses
            - evaluation: For analyzing learning progress
            - personalization: For personalizing responses
            
            Determine:
            1. Is the query specific enough to proceed, or should we ask clarifying questions?
               - VAGUE queries like "tell me about [country]", "what about [country]", "[country] info", "what can you say about [country]" MUST ask for clarification
               - SPECIFIC queries like "places to eat in [country]", "song recommendations for [country]", "news about [country]" can proceed
            2. What is the user's intent? (learn_language, cultural_info, pronunciation_help, travel_advice, etc.)
            3. What country/culture are they interested in?
            4. Which specific data sources should be queried based on their intent?
            5. Which agents should be activated? (ALWAYS include 'data_retrieval' if any data sources are needed)
            6. Does this require real-time voice processing?
            7. Confidence level (0-1)
            
            CRITICAL: If the query is vague or general, you MUST set "needs_clarification": true and provide a clarifying question. DO NOT proceed with data retrieval for vague queries.
            
            Respond in JSON format:
            {{
                "intent": "intent_type",
                "target_country": "country_name",
                "data_sources": ["source1", "source2"],
                "agents_to_activate": ["agent1", "agent2"],
                "requires_voice": true/false,
                "confidence": 0.9,
                "reasoning": "explanation",
                "needs_clarification": false,
                "clarifying_question": "What specific aspect would you like to know about?"
            }}
            
            IMPORTANT: For vague queries, set needs_clarification: true and data_sources: [], agents_to_activate: ["conversation"]
            """
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
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

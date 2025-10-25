"""
Evaluation Agent
Analyzes interactions and provides feedback on learning progress
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


class EvaluationAgent(BaseAgent):
    """
    Analyzes interactions and provides feedback on:
    - Learning progress
    - Engagement level
    - Areas for improvement
    - Personalized recommendations
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("Evaluation", anthropic_api_key)
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Analyzes interaction and provides feedback
        """
        try:
            interaction_data = input_data.get("interaction_data", {})
            user_profile = input_data.get("user_profile", {})
            session_context = input_data.get("session_context", {})
            
            logger.info(f"[Evaluation] Analyzing interaction")
            
            evaluation = await self._evaluate_interaction(
                interaction_data, 
                user_profile,
                session_context
            )
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data=evaluation,
                confidence=evaluation.get("confidence", 0.8),
                reasoning=evaluation.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"[Evaluation] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _evaluate_interaction(self, interaction: Dict, profile: Dict, context: Dict) -> Dict:
        """Use Claude via Anthropic API to evaluate interaction"""
        try:
            prompt = f"""
            You are an AI learning evaluation expert. Analyze this interaction for learning progress.
            
            Interaction Data: {json.dumps(interaction)}
            User Profile: {json.dumps(profile)}
            Session Context: {json.dumps(context)}
            
            Evaluate:
            1. Learning progress indicators
            2. Engagement level
            3. Areas for improvement
            4. Personalized recommendations
            5. Next learning steps
            
            Respond in JSON:
            {{
                "learning_progress": {{
                    "language_improvement": "excellent/good/needs_work",
                    "cultural_understanding": "excellent/good/needs_work",
                    "engagement_level": "high/medium/low"
                }},
                "strengths": ["strength1", "strength2"],
                "improvement_areas": ["area1", "area2"],
                "recommendations": [
                    {{"type": "practice/explore/review", "description": "...", "priority": "high/medium/low"}}
                ],
                "next_steps": ["step1", "step2"],
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
                        evaluation_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = evaluation_text.find('{')
            end_idx = evaluation_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(evaluation_text[start_idx:end_idx])
                    
        except Exception as e:
            logger.error(f"[Evaluation] Error: {str(e)}")
        
        return {
            "learning_progress": {
                "language_improvement": "unknown",
                "cultural_understanding": "unknown",
                "engagement_level": "medium"
            },
            "strengths": [],
            "improvement_areas": [],
            "recommendations": [],
            "next_steps": [],
            "confidence": 0.3,
            "reasoning": "Unable to evaluate"
        }

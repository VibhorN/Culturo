"""
Simplified Arize Integration for Query-Level Logging
Logs one row per query with agent evaluations and scores
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from arize.api import Client
    from arize.utils.types import ModelTypes, Environments
    ARIZE_AVAILABLE = True
except ImportError:
    ARIZE_AVAILABLE = False
    logging.warning("Arize dependencies not installed. Run: pip install arize")

logger = logging.getLogger(__name__)

class SimplifiedArizeIntegration:
    """
    Simplified Arize integration that logs one row per query
    with comprehensive agent evaluation data
    """
    
    def __init__(self):
        self.client = None
        self.space_id = os.getenv("ARIZE_SPACE_ID")
        self.api_key = os.getenv("ARIZE_API_KEY")
        self.project_name = os.getenv("ARIZE_PROJECT_NAME", "lingua-cal-agents")
        self.environment = os.getenv("ARIZE_ENVIRONMENT", "development")
        self.enabled = ARIZE_AVAILABLE and self.space_id and self.api_key
        
        if self.enabled:
            self._initialize_arize()
        else:
            logger.warning("Simplified Arize integration disabled. Missing credentials or dependencies.")
    
    def _initialize_arize(self):
        """Initialize Arize client"""
        try:
            self.client = Client(
                space_key=self.space_id,
                api_key=self.api_key
            )
            logger.info(f"Simplified Arize integration initialized for project: {self.project_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Arize: {str(e)}")
            self.enabled = False
    
    async def log_query_with_agent_evaluations(self,
                                             user_id: str,
                                             question: str,
                                             response: str,
                                             agents_used: Dict[str, Dict[str, Any]],
                                             anthropic_client=None):
        """
        Log one row per query with agent evaluations
        
        Args:
            user_id: User identifier
            question: User's question
            response: Final response
            agents_used: Dict of {agent_name: {output_data, execution_time, confidence, status}}
            anthropic_client: Anthropic client for evaluations
        """
        if not self.enabled:
            logger.warning("Arize not enabled, skipping query logging")
            return
        
        try:
            # Evaluate each agent using Anthropic
            agent_evaluations = {}
            for agent_name, agent_data in agents_used.items():
                evaluation = await self._evaluate_agent_with_anthropic(
                    agent_name, agent_data, question, anthropic_client
                )
                agent_evaluations[agent_name] = evaluation
            
            # Prepare consolidated row data
            row_data = {
                # Basic query info
                "user_id": user_id,
                "question": question,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "total_agents_used": len(agents_used),
                
                # Agent usage columns
                "agents_used": list(agents_used.keys()),
                "agent_count": len(agents_used),
            }
            
            # Add individual agent data
            for agent_name, agent_data in agents_used.items():
                evaluation = agent_evaluations.get(agent_name, {})
                
                # Agent usage info
                row_data[f"{agent_name}_used"] = True
                row_data[f"{agent_name}_execution_time"] = agent_data.get("execution_time", 0)
                row_data[f"{agent_name}_confidence"] = agent_data.get("confidence", 0)
                row_data[f"{agent_name}_status"] = agent_data.get("status", "unknown")
                
                # Agent evaluation scores
                row_data[f"{agent_name}_score"] = evaluation.get("score", 0.0)
                row_data[f"{agent_name}_score_explanation"] = evaluation.get("explanation", "No evaluation")
                row_data[f"{agent_name}_relevance_score"] = evaluation.get("relevance_score", 0.0)
                row_data[f"{agent_name}_quality_score"] = evaluation.get("quality_score", 0.0)
                row_data[f"{agent_name}_helpfulness_score"] = evaluation.get("helpfulness_score", 0.0)
                
                # Why this agent was used
                row_data[f"{agent_name}_usage_reason"] = agent_data.get("usage_reason", "Not specified")
            
            # Calculate overall query score
            overall_score = self._calculate_overall_score(agent_evaluations)
            row_data["overall_query_score"] = overall_score
            
            # Log to Arize
            self.client.log(
                model_id="query_evaluations",
                model_version="1.0",
                model_type=ModelTypes.REGRESSION,
                environment=Environments.PRODUCTION if self.environment == "production" else Environments.TRAINING,
                prediction_id=f"{user_id}_{int(time.time())}",
                features=row_data,
                prediction_label=overall_score,
                actual_label=overall_score,  # Using same value for both
                tags={
                    "user_id": user_id,
                    "query_type": "cultural_assistance",
                    "agents_count": len(agents_used)
                }
            )
            
            logger.info(f"Logged query evaluation for user {user_id}: Overall Score = {overall_score:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to log query evaluation: {str(e)}")
    
    async def _evaluate_agent_with_anthropic(self, agent_name: str, agent_data: Dict, 
                                           question: str, anthropic_client) -> Dict[str, Any]:
        """
        Use Anthropic to evaluate an agent's performance
        """
        if not anthropic_client:
            logger.warning("No Anthropic client provided for evaluation")
            return {"score": 0.5, "explanation": "No evaluation available"}
        
        try:
            # Get agent's output
            agent_output = agent_data.get("output_data", {})
            agent_response = agent_output.get("response", "")
            agent_confidence = agent_data.get("confidence", 0)
            agent_status = agent_data.get("status", "unknown")
            
            # Create evaluation prompt
            evaluation_prompt = f"""
You are an expert evaluator of AI agent performance. Evaluate this agent's output against what it should have done.

AGENT: {agent_name}
USER QUESTION: {question}
AGENT RESPONSE: {agent_response}
AGENT CONFIDENCE: {agent_confidence}
AGENT STATUS: {agent_status}

EVALUATION CRITERIA:
1. Relevance (0-1): How well does the response address the user's question?
2. Quality (0-1): How complete, accurate, and well-structured is the response?
3. Helpfulness (0-1): How useful and actionable is the response for the user?

Respond in JSON format:
{{
    "relevance_score": 0.0-1.0,
    "quality_score": 0.0-1.0,
    "helpfulness_score": 0.0-1.0,
    "overall_score": 0.0-1.0,
    "explanation": "Detailed explanation of the evaluation",
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"]
}}
"""
            
            # Call Anthropic
            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": evaluation_prompt}]
            )
            
            # Parse response
            evaluation_text = response.content[0].text
            start_idx = evaluation_text.find('{')
            end_idx = evaluation_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                evaluation_json = evaluation_text[start_idx:end_idx]
                evaluation = json.loads(evaluation_json)
                
                # Ensure all required fields exist
                return {
                    "score": evaluation.get("overall_score", 0.5),
                    "explanation": evaluation.get("explanation", "No explanation provided"),
                    "relevance_score": evaluation.get("relevance_score", 0.5),
                    "quality_score": evaluation.get("quality_score", 0.5),
                    "helpfulness_score": evaluation.get("helpfulness_score", 0.5),
                    "strengths": evaluation.get("strengths", []),
                    "improvements": evaluation.get("improvements", [])
                }
            else:
                logger.error(f"Could not parse Anthropic evaluation response for {agent_name}")
                return {"score": 0.5, "explanation": "Failed to parse evaluation"}
                
        except Exception as e:
            logger.error(f"Failed to evaluate agent {agent_name} with Anthropic: {str(e)}")
            return {"score": 0.5, "explanation": f"Evaluation failed: {str(e)}"}
    
    def _calculate_overall_score(self, agent_evaluations: Dict[str, Dict]) -> float:
        """Calculate overall query score from agent evaluations"""
        if not agent_evaluations:
            return 0.0
        
        scores = [eval_data.get("score", 0.0) for eval_data in agent_evaluations.values()]
        return sum(scores) / len(scores) if scores else 0.0

# Global instance
simplified_arize = SimplifiedArizeIntegration()

# Convenience function
async def log_query_evaluation(user_id: str, question: str, response: str, 
                             agents_used: Dict[str, Dict[str, Any]], 
                             anthropic_client=None):
    """Convenience function to log query evaluation"""
    await simplified_arize.log_query_with_agent_evaluations(
        user_id, question, response, agents_used, anthropic_client
    )

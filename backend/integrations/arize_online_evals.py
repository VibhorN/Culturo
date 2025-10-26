"""
Arize Online Evals Integration
Creates proper columns for each agent's scores and explanations
"""

import os
import logging
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from arize.api import Client
    from arize.utils.types import ModelTypes, Environments
    ARIZE_AVAILABLE = True
except ImportError:
    ARIZE_AVAILABLE = False
    logging.warning("Arize dependencies not installed. Run: pip install arize")

logger = logging.getLogger(__name__)

class ArizeOnlineEvalsIntegration:
    """
    Arize Online Evals integration for agent evaluations with proper columns
    """
    
    def __init__(self):
        self.client = None
        self.enabled = False
        self.space_id = os.getenv("ARIZE_SPACE_ID")
        self.api_key = os.getenv("ARIZE_API_KEY")
        self.project_name = os.getenv("ARIZE_PROJECT_NAME", "lingua-cal-agents")
        self.environment = os.getenv("ARIZE_ENVIRONMENT", "development")
        
        if ARIZE_AVAILABLE and self.space_id and self.api_key:
            self._initialize_arize()
        else:
            logger.warning("Arize Online Evals not enabled. Missing credentials or dependencies.")
    
    def _initialize_arize(self):
        """Initialize Arize client"""
        try:
            self.client = Client(
                space_id=self.space_id,
                api_key=self.api_key
            )
            self.enabled = True
            logger.info(f"Arize Online Evals initialized for project: {self.project_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Arize Online Evals: {str(e)}")
            self.enabled = False
    
    def log_query_evaluation(self, 
                           user_id: str,
                           question: str, 
                           response: str,
                           agents_used: Dict[str, Dict[str, Any]],
                           anthropic_client: Any = None):
        """
        Log a complete query evaluation with proper columns for each agent
        """
        if not self.enabled:
            logger.warning("Arize Online Evals not enabled, skipping query logging")
            return
        
        try:
            session_id = f"{user_id}_{int(time.time())}"
            
            # Prepare base features
            features = {
                "user_id": user_id,
                "question": question,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "total_agents_used": len(agents_used)
            }
            
            overall_scores = []
            
            # Process each agent and create dedicated columns
            for agent_name, agent_data in agents_used.items():
                agent_output_data = agent_data.get("output_data", {})
                agent_execution_time = agent_data.get("execution_time", 0)
                agent_confidence = agent_data.get("confidence", 0)
                agent_status = agent_data.get("status", "success")
                agent_usage_reason = agent_data.get("usage_reason", "N/A")
                
                # Evaluate agent if Anthropic client is available
                if anthropic_client:
                    try:
                        evaluation_result = self._evaluate_agent_with_anthropic(
                            anthropic_client, agent_name, question, agent_output_data
                        )
                        
                        # Add agent-specific columns
                        features[f"{agent_name}_used"] = True
                        features[f"{agent_name}_usage_reason"] = agent_usage_reason
                        features[f"{agent_name}_execution_time_ms"] = agent_execution_time * 1000
                        features[f"{agent_name}_confidence"] = agent_confidence
                        features[f"{agent_name}_status"] = agent_status
                        features[f"{agent_name}_score"] = evaluation_result["score"]
                        features[f"{agent_name}_score_explanation"] = evaluation_result["explanation"]
                        features[f"{agent_name}_relevance_score"] = evaluation_result["relevance_score"]
                        features[f"{agent_name}_quality_score"] = evaluation_result["quality_score"]
                        features[f"{agent_name}_helpfulness_score"] = evaluation_result["helpfulness_score"]
                        features[f"{agent_name}_strengths"] = json.dumps(evaluation_result["strengths"])
                        features[f"{agent_name}_improvements"] = json.dumps(evaluation_result["improvements"])
                        
                        overall_scores.append(evaluation_result["score"])
                        
                    except Exception as eval_error:
                        logger.error(f"Failed to evaluate agent {agent_name}: {str(eval_error)}")
                        # Add fallback evaluation columns
                        features[f"{agent_name}_used"] = True
                        features[f"{agent_name}_usage_reason"] = agent_usage_reason
                        features[f"{agent_name}_execution_time_ms"] = agent_execution_time * 1000
                        features[f"{agent_name}_confidence"] = agent_confidence
                        features[f"{agent_name}_status"] = agent_status
                        features[f"{agent_name}_score"] = 0.5
                        features[f"{agent_name}_score_explanation"] = f"Evaluation failed: {str(eval_error)}"
                        features[f"{agent_name}_relevance_score"] = 0.5
                        features[f"{agent_name}_quality_score"] = 0.5
                        features[f"{agent_name}_helpfulness_score"] = 0.5
                        features[f"{agent_name}_strengths"] = json.dumps(["N/A"])
                        features[f"{agent_name}_improvements"] = json.dumps(["Evaluation system unavailable"])
                        
                        overall_scores.append(0.5)
                else:
                    # Add fallback evaluation columns
                    features[f"{agent_name}_used"] = True
                    features[f"{agent_name}_usage_reason"] = agent_usage_reason
                    features[f"{agent_name}_execution_time_ms"] = agent_execution_time * 1000
                    features[f"{agent_name}_confidence"] = agent_confidence
                    features[f"{agent_name}_status"] = agent_status
                    features[f"{agent_name}_score"] = 0.5
                    features[f"{agent_name}_score_explanation"] = "No Anthropic client available for evaluation"
                    features[f"{agent_name}_relevance_score"] = 0.5
                    features[f"{agent_name}_quality_score"] = 0.5
                    features[f"{agent_name}_helpfulness_score"] = 0.5
                    features[f"{agent_name}_strengths"] = json.dumps(["N/A"])
                    features[f"{agent_name}_improvements"] = json.dumps(["Ensure Anthropic client is configured"])
                    
                    overall_scores.append(0.5)
            
            # Calculate overall query score
            overall_query_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
            features["overall_query_score"] = overall_query_score
            
            # Log to Arize with proper model for Online Evals
            self.client.log(
                model_id="agent_evaluations",
                model_version="1.0",
                model_type=ModelTypes.REGRESSION,
                environment=Environments.PRODUCTION if self.environment == "production" else Environments.TRAINING,
                prediction_id=session_id,
                features=features,
                prediction_label=overall_query_score,
                actual_label=overall_query_score,
                tags={
                    "user_id": user_id,
                    "query_type": "general",
                    "agents_used": ",".join(agents_used.keys())
                }
            )
            
            logger.info(f"Logged query evaluation for user {user_id}: Overall Score = {overall_query_score:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to log query evaluation to Arize Online Evals: {str(e)}")
    
    def _evaluate_agent_with_anthropic(self, anthropic_client: Any, agent_name: str, 
                                     user_question: str, agent_output: Dict) -> Dict:
        """
        Evaluates an agent's output using Anthropic Claude-3-Haiku
        """
        prompt = f"""You are an AI agent evaluator. Your task is to evaluate the performance of a specific AI agent based on its output in response to a user's question.

Agent Name: {agent_name}
User Question: "{user_question}"
Agent Output: {json.dumps(agent_output, indent=2)}

Evaluate the agent's output based on the following criteria (score 0-1, 1 being excellent):
1. **Relevance**: How well did the agent's output address the user's question and the agent's intended purpose?
2. **Quality**: Is the output well-structured, clear, coherent, and free of errors?
3. **Helpfulness**: Does the output provide valuable, actionable, or insightful information to the user?

Provide an overall score (0-1) and a detailed explanation for each criterion, including specific strengths and areas for improvement.

Respond in JSON format with the following structure:
{{
    "overall_score": 0.85,
    "explanation": "Overall assessment of the agent's performance.",
    "relevance_score": 0.9,
    "relevance_explanation": "Explanation for relevance score.",
    "quality_score": 0.8,
    "quality_explanation": "Explanation for quality score.",
    "helpfulness_score": 0.85,
    "helpfulness_explanation": "Explanation for helpfulness score.",
    "strengths": ["Specific strength 1", "Specific strength 2"],
    "improvements": ["Area for improvement 1", "Area for improvement 2"]
}}
"""
        
        try:
            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            evaluation_json = response.content[0].text
            
            # Attempt to parse JSON, handling potential malformed output
            start_idx = evaluation_json.find('{')
            end_idx = evaluation_json.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                evaluation = json.loads(evaluation_json[start_idx:end_idx])
                
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

# Global instance
arize_online_evals = ArizeOnlineEvalsIntegration()

def log_query_evaluation(user_id: str, question: str, response: str, 
                        agents_used: Dict[str, Dict[str, Any]], anthropic_client: Any = None):
    """Convenience function to log query evaluation"""
    arize_online_evals.log_query_evaluation(user_id, question, response, agents_used, anthropic_client)

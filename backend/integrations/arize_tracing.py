"""
Arize OpenTelemetry Tracing Integration
Logs all agent interactions to the lingua-cal-agents project using LLM Tracing
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from arize.otel import register
    from openinference.instrumentation.anthropic import AnthropicInstrumentor
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    ARIZE_TRACING_AVAILABLE = True
except ImportError:
    ARIZE_TRACING_AVAILABLE = False
    logging.warning("Arize tracing dependencies not installed. Run: pip install openinference-instrumentation-anthropic anthropic arize-otel opentelemetry-sdk")

logger = logging.getLogger(__name__)

class ArizeTracingIntegration:
    """
    Arize OpenTelemetry tracing integration for agent evaluations
    """
    
    def __init__(self):
        self.tracer = None
        self.enabled = False
        self.space_id = os.getenv("ARIZE_SPACE_ID")
        self.api_key = os.getenv("ARIZE_API_KEY")
        self.project_name = os.getenv("ARIZE_PROJECT_NAME", "lingua-cal-agents")
        
        if ARIZE_TRACING_AVAILABLE and self.space_id and self.api_key:
            self._initialize_tracing()
        else:
            logger.warning("Arize tracing not enabled. Missing credentials or dependencies.")
    
    def _initialize_tracing(self):
        """Initialize Arize OpenTelemetry tracing"""
        try:
            # Setup OTel via Arize convenience function
            tracer_provider = register(
                space_id=self.space_id,
                api_key=self.api_key,
                project_name=self.project_name,
            )
            
            # Import and setup Anthropic instrumentor
            AnthropicInstrumentor().instrument(tracer_provider=tracer_provider)
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__)
            self.enabled = True
            
            logger.info(f"Arize tracing initialized for project: {self.project_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Arize tracing: {str(e)}")
            self.enabled = False
    
    def log_query_evaluation(self, 
                           user_id: str,
                           question: str, 
                           response: str,
                           agents_used: Dict[str, Dict[str, Any]],
                           anthropic_client: Any = None):
        """
        Log a complete query evaluation as a trace with spans for each agent
        """
        if not self.enabled:
            logger.warning("Arize tracing not enabled, skipping query logging")
            return
        
        try:
            # Create a root span for the entire query
            with self.tracer.start_as_current_span("query_evaluation") as root_span:
                # Set root span attributes
                root_span.set_attribute("user_id", user_id)
                root_span.set_attribute("question", question)
                root_span.set_attribute("response", response)
                root_span.set_attribute("total_agents_used", len(agents_used))
                root_span.set_attribute("timestamp", datetime.now().isoformat())
                
                # Calculate overall score
                overall_scores = []
                
                # Create spans for each agent
                for agent_name, agent_data in agents_used.items():
                    agent_output_data = agent_data.get("output_data", {})
                    agent_execution_time = agent_data.get("execution_time", 0)
                    agent_confidence = agent_data.get("confidence", 0)
                    agent_status = agent_data.get("status", "success")
                    agent_usage_reason = agent_data.get("usage_reason", "N/A")
                    
                    # Create agent span
                    with self.tracer.start_as_current_span(f"agent_{agent_name}") as agent_span:
                        # Set agent span attributes
                        agent_span.set_attribute("agent_name", agent_name)
                        agent_span.set_attribute("agent_usage_reason", agent_usage_reason)
                        agent_span.set_attribute("agent_execution_time_ms", agent_execution_time * 1000)
                        agent_span.set_attribute("agent_confidence", agent_confidence)
                        agent_span.set_attribute("agent_status", agent_status)
                        
                        # Evaluate agent if Anthropic client is available
                        if anthropic_client:
                            try:
                                evaluation_result = self._evaluate_agent_with_anthropic(
                                    anthropic_client, agent_name, question, agent_output_data
                                )
                                
                                # Set evaluation attributes
                                agent_span.set_attribute("agent_score", evaluation_result["score"])
                                agent_span.set_attribute("agent_score_explanation", evaluation_result["explanation"])
                                agent_span.set_attribute("agent_relevance_score", evaluation_result["relevance_score"])
                                agent_span.set_attribute("agent_quality_score", evaluation_result["quality_score"])
                                agent_span.set_attribute("agent_helpfulness_score", evaluation_result["helpfulness_score"])
                                agent_span.set_attribute("agent_strengths", str(evaluation_result["strengths"]))
                                agent_span.set_attribute("agent_improvements", str(evaluation_result["improvements"]))
                                
                                overall_scores.append(evaluation_result["score"])
                                
                            except Exception as eval_error:
                                logger.error(f"Failed to evaluate agent {agent_name}: {str(eval_error)}")
                                # Set fallback evaluation
                                agent_span.set_attribute("agent_score", 0.5)
                                agent_span.set_attribute("agent_score_explanation", f"Evaluation failed: {str(eval_error)}")
                                overall_scores.append(0.5)
                        else:
                            # Set fallback evaluation
                            agent_span.set_attribute("agent_score", 0.5)
                            agent_span.set_attribute("agent_score_explanation", "No Anthropic client available for evaluation")
                            overall_scores.append(0.5)
                        
                        # Set span status
                        if agent_status == "success":
                            agent_span.set_status(Status(StatusCode.OK))
                        else:
                            agent_span.set_status(Status(StatusCode.ERROR, f"Agent {agent_name} failed"))
                
                # Set overall query score
                overall_query_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
                root_span.set_attribute("overall_query_score", overall_query_score)
                
                # Set root span status
                root_span.set_status(Status(StatusCode.OK))
                
                logger.info(f"Logged query evaluation trace for user {user_id}: Overall Score = {overall_query_score:.2f}")
                
        except Exception as e:
            logger.error(f"Failed to log query evaluation trace: {str(e)}")
    
    def _evaluate_agent_with_anthropic(self, anthropic_client: Any, agent_name: str, 
                                     user_question: str, agent_output: Dict) -> Dict:
        """
        Evaluates an agent's output using Anthropic Claude-3-Haiku
        """
        import json
        
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
arize_tracing = ArizeTracingIntegration()

def log_query_evaluation(user_id: str, question: str, response: str, 
                        agents_used: Dict[str, Dict[str, Any]], anthropic_client: Any = None):
    """Convenience function to log query evaluation"""
    arize_tracing.log_query_evaluation(user_id, question, response, agents_used, anthropic_client)

"""
Arize AI Integration for Agent Evaluation and Observability
Provides comprehensive monitoring, tracing, and evaluation for all agents
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict

try:
    from arize.otel import register
    from arize.api import Client
    from arize.utils.types import ModelTypes, Environments
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    ARIZE_AVAILABLE = True
except ImportError:
    ARIZE_AVAILABLE = False
    logging.warning("Arize dependencies not installed. Run: pip install arize-otel")

logger = logging.getLogger(__name__)

@dataclass
class AgentEvaluationMetrics:
    """Structured metrics for agent evaluation"""
    agent_name: str
    user_id: str
    session_id: str
    timestamp: str
    input_tokens: int
    output_tokens: int
    execution_time_ms: float
    confidence_score: float
    success_rate: float
    response_quality_score: float
    user_satisfaction_score: Optional[float] = None
    error_rate: float = 0.0
    retry_count: int = 0
    cost_usd: Optional[float] = None
    metadata: Dict[str, Any] = None

class ArizeIntegration:
    """
    Comprehensive Arize integration for agent evaluation and observability
    """
    
    def __init__(self):
        self.client = None
        self.tracer = None
        self.space_id = os.getenv("ARIZE_SPACE_ID")
        self.api_key = os.getenv("ARIZE_API_KEY")
        self.project_name = os.getenv("ARIZE_PROJECT_NAME", "lingua-cal-agents")
        self.environment = os.getenv("ARIZE_ENVIRONMENT", "development")
        self.enabled = ARIZE_AVAILABLE and self.space_id and self.api_key
        
        if self.enabled:
            self._initialize_arize()
        else:
            logger.warning("Arize integration disabled. Missing credentials or dependencies.")
    
    def _initialize_arize(self):
        """Initialize Arize client and tracing"""
        try:
            # Register OpenTelemetry with Arize (as shown in the screenshot)
            tracer_provider = register(
                space_id=self.space_id,
                api_key=self.api_key,
                project_name=self.project_name
            )
            
            # Initialize Arize client
            self.client = Client(
                space_key=self.space_id,
                api_key=self.api_key
            )
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__)
            
            # Instrument HTTP clients
            AioHttpClientInstrumentor().instrument()
            RequestsInstrumentor().instrument()
            
            logger.info(f"Arize integration initialized for project: {self.project_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Arize: {str(e)}")
            self.enabled = False
    
    def log_agent_execution(self, 
                          agent_name: str,
                          user_id: str,
                          session_id: str,
                          input_data: Dict[str, Any],
                          output_data: Dict[str, Any],
                          execution_time: float,
                          confidence: float,
                          status: str = "success",
                          error_message: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None):
        """
        Log agent execution to Arize for evaluation and monitoring
        """
        if not self.enabled:
            return
        
        try:
            # Create evaluation metrics
            metrics = AgentEvaluationMetrics(
                agent_name=agent_name,
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.now().isoformat(),
                input_tokens=self._count_tokens(input_data),
                output_tokens=self._count_tokens(output_data),
                execution_time_ms=execution_time * 1000,
                confidence_score=confidence,
                success_rate=1.0 if status == "success" else 0.0,
                response_quality_score=self._calculate_quality_score(output_data),
                error_rate=0.0 if status == "success" else 1.0,
                metadata=metadata or {}
            )
            
            # Log to Arize
            self._log_to_arize(metrics, input_data, output_data)
            
            # Create trace span
            self._create_trace_span(agent_name, input_data, output_data, execution_time, status)
            
        except Exception as e:
            logger.error(f"Failed to log agent execution to Arize: {str(e)}")
    
    def log_evaluation_result(self,
                            agent_name: str,
                            user_id: str,
                            evaluation_type: str,
                            evaluation_data: Dict[str, Any],
                            score: float,
                            feedback: Optional[str] = None):
        """
        Log evaluation results for agent performance analysis
        """
        if not self.enabled:
            return
        
        try:
            # Prepare evaluation data for Arize
            evaluation_record = {
                "agent_name": agent_name,
                "user_id": user_id,
                "evaluation_type": evaluation_type,
                "score": score,
                "timestamp": datetime.now().isoformat(),
                "feedback": feedback,
                "evaluation_data": evaluation_data
            }
            
            # Log evaluation to Arize
            self.client.log(
                model_id=f"{agent_name}_evaluations",
                model_version="1.0",
                model_type=ModelTypes.REGRESSION,
                environment=Environments.PRODUCTION if self.environment == "production" else Environments.TRAINING,
                prediction_id=f"{user_id}_{int(time.time())}",
                features=evaluation_data,
                prediction_label=score,
                actual_label=score,  # For now, using same value
                tags={"evaluation_type": evaluation_type, "agent": agent_name}
            )
            
            logger.info(f"Logged evaluation for {agent_name}: {evaluation_type} = {score}")
            
        except Exception as e:
            logger.error(f"Failed to log evaluation result: {str(e)}")
    
    def log_user_interaction(self,
                           user_id: str,
                           interaction_type: str,
                           interaction_data: Dict[str, Any],
                           satisfaction_score: Optional[float] = None):
        """
        Log user interactions for engagement analysis
        """
        if not self.enabled:
            return
        
        try:
            interaction_record = {
                "user_id": user_id,
                "interaction_type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "satisfaction_score": satisfaction_score,
                "interaction_data": interaction_data
            }
            
            # Log to Arize for user behavior analysis
            self.client.log(
                model_id="user_interactions",
                model_version="1.0",
                model_type=ModelTypes.REGRESSION,
                environment=Environments.PRODUCTION if self.environment == "production" else Environments.TRAINING,
                prediction_id=f"{user_id}_{int(time.time())}",
                features=interaction_data,
                prediction_label=satisfaction_score or 0.0,
                tags={"user_id": user_id, "interaction_type": interaction_type}
            )
            
        except Exception as e:
            logger.error(f"Failed to log user interaction: {str(e)}")
    
    def log_consolidated_chat_evaluation(self,
                                      chat_session_id: str,
                                      user_id: str,
                                      chat_input: str,
                                      agent_evaluations: Dict[str, Dict[str, Any]],
                                      overall_chat_score: float,
                                      chat_summary: str):
        """
        Log consolidated chat evaluation with one row per chat session
        Each row contains scores and reasons for all agents used in that chat
        """
        if not self.enabled:
            return
        
        try:
            # Prepare consolidated evaluation data
            consolidated_data = {
                "chat_session_id": chat_session_id,
                "user_id": user_id,
                "chat_input": chat_input,
                "chat_summary": chat_summary,
                "overall_chat_score": overall_chat_score,
                "timestamp": datetime.now().isoformat(),
                "agents_used": list(agent_evaluations.keys()),
                "total_agents_used": len(agent_evaluations)
            }
            
            # Add individual agent scores and reasons
            for agent_name, evaluation in agent_evaluations.items():
                consolidated_data[f"{agent_name}_score"] = evaluation.get("overall_score", 0.0)
                consolidated_data[f"{agent_name}_reason"] = evaluation.get("overall_reason", "No evaluation provided")
                consolidated_data[f"{agent_name}_response_quality"] = evaluation.get("response_quality_score", 0.0)
                consolidated_data[f"{agent_name}_performance"] = evaluation.get("performance_score", 0.0)
                consolidated_data[f"{agent_name}_accuracy"] = evaluation.get("accuracy_score", 0.0)
                consolidated_data[f"{agent_name}_relevance"] = evaluation.get("relevance_score", 0.0)
                consolidated_data[f"{agent_name}_user_experience"] = evaluation.get("user_experience_score", 0.0)
                consolidated_data[f"{agent_name}_execution_time"] = evaluation.get("execution_time", 0.0)
                consolidated_data[f"{agent_name}_confidence"] = evaluation.get("confidence", 0.0)
                consolidated_data[f"{agent_name}_status"] = evaluation.get("status", "unknown")
            
            # Log consolidated evaluation to Arize
            self.client.log(
                model_id="consolidated_chat_evaluations",
                model_version="1.0",
                model_type=ModelTypes.REGRESSION,
                environment=Environments.PRODUCTION if self.environment == "production" else Environments.TRAINING,
                prediction_id=f"{chat_session_id}_{int(time.time())}",
                features=consolidated_data,
                prediction_label=overall_chat_score,
                actual_label=overall_chat_score,
                tags={
                    "chat_session_id": chat_session_id,
                    "user_id": user_id,
                    "evaluation_type": "consolidated_chat",
                    "agents_used": ",".join(agent_evaluations.keys())
                }
            )
            
            logger.info(f"Logged consolidated chat evaluation for session {chat_session_id}: Overall Score = {overall_chat_score:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to log consolidated chat evaluation: {str(e)}")
    
    def log_comprehensive_agent_evaluation(self,
                                         agent_name: str,
                                         user_id: str,
                                         session_id: str,
                                         input_data: Dict[str, Any],
                                         output_data: Dict[str, Any],
                                         execution_time: float,
                                         confidence: float,
                                         status: str = "success",
                                         error_message: Optional[str] = None,
                                         metadata: Optional[Dict[str, Any]] = None):
        """
        Log comprehensive agent evaluation with detailed scores and reasoning
        """
        if not self.enabled:
            return
        
        try:
            # Calculate comprehensive evaluation scores
            evaluation_scores = self._calculate_comprehensive_scores(
                agent_name, input_data, output_data, execution_time, confidence, status
            )
            
            # Generate detailed reasoning for each score
            evaluation_reasoning = self._generate_evaluation_reasoning(
                agent_name, input_data, output_data, evaluation_scores, status
            )
            
            # Prepare comprehensive evaluation data (flatten for Arize compatibility)
            evaluation_data = {
                "agent_name": agent_name,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "execution_time_ms": execution_time * 1000,
                "status": status,
                "error_message": error_message or "",
                # Flatten input data
                "user_question": str(input_data.get("user_question", "")),
                "input_context": str(input_data.get("context", "")),
                "input_language": str(input_data.get("language", "")),
                "input_word": str(input_data.get("word", "")),
                "input_difficulty": str(input_data.get("difficulty", "")),
                # Flatten output data
                "agent_response": str(output_data.get("response", "")),
                "output_confidence": float(output_data.get("confidence", 0.0)),
                "output_reasoning": str(output_data.get("reasoning", "")),
                "output_language_detected": str(output_data.get("language_detected", "")),
                "output_pronunciation": str(output_data.get("pronunciation", "")),
                # Add evaluation scores and reasoning
                **evaluation_scores,
                **evaluation_reasoning,
                **(metadata or {})
            }
            
            # Log comprehensive evaluation to Arize
            self.client.log(
                model_id=f"{agent_name}_comprehensive_evaluation",
                model_version="1.0",
                model_type=ModelTypes.REGRESSION,
                environment=Environments.PRODUCTION if self.environment == "production" else Environments.TRAINING,
                prediction_id=f"{user_id}_{session_id}_{int(time.time())}",
                features=evaluation_data,
                prediction_label=evaluation_scores["overall_score"],
                actual_label=evaluation_scores["overall_score"],
                tags={
                    "agent_name": agent_name,
                    "user_id": user_id,
                    "session_id": session_id,
                    "evaluation_type": "comprehensive"
                }
            )
            
            logger.info(f"Logged comprehensive evaluation for {agent_name}: Overall Score = {evaluation_scores['overall_score']:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to log comprehensive agent evaluation: {str(e)}")
    
    def _calculate_comprehensive_scores(self, agent_name: str, input_data: Dict, output_data: Dict, 
                                       execution_time: float, confidence: float, status: str) -> Dict[str, float]:
        """Calculate comprehensive evaluation scores for an agent"""
        
        # Response Quality Score (0.0-1.0)
        response_quality = self._calculate_response_quality_score(output_data, confidence)
        
        # Performance Score (0.0-1.0) - based on execution time and efficiency
        performance_score = self._calculate_performance_score(execution_time, agent_name)
        
        # Accuracy Score (0.0-1.0) - based on confidence and status
        accuracy_score = self._calculate_accuracy_score(confidence, status)
        
        # Relevance Score (0.0-1.0) - how well the response matches the input
        relevance_score = self._calculate_relevance_score(input_data, output_data)
        
        # User Experience Score (0.0-1.0) - based on response completeness and helpfulness
        user_experience_score = self._calculate_user_experience_score(output_data, input_data)
        
        # Overall Score (weighted average)
        overall_score = (
            response_quality * 0.25 +
            performance_score * 0.20 +
            accuracy_score * 0.25 +
            relevance_score * 0.15 +
            user_experience_score * 0.15
        )
        
        return {
            "response_quality_score": response_quality,
            "performance_score": performance_score,
            "accuracy_score": accuracy_score,
            "relevance_score": relevance_score,
            "user_experience_score": user_experience_score,
            "overall_score": overall_score,
            "confidence_score": confidence,
            "execution_time_score": max(0, 1.0 - (execution_time / 10.0))  # Penalize slow responses
        }
    
    def _generate_evaluation_reasoning(self, agent_name: str, input_data: Dict, output_data: Dict, 
                                     scores: Dict[str, float], status: str) -> Dict[str, str]:
        """Generate detailed reasoning for each evaluation score"""
        
        reasoning = {}
        
        # Response Quality Reasoning
        if scores["response_quality_score"] >= 0.8:
            reasoning["response_quality_reason"] = f"{agent_name} provided a comprehensive, well-structured response with clear information and helpful details."
        elif scores["response_quality_score"] >= 0.6:
            reasoning["response_quality_reason"] = f"{agent_name} provided a good response with adequate information, though it could be more detailed."
        else:
            reasoning["response_quality_reason"] = f"{agent_name} provided a basic response that lacks depth or helpful information."
        
        # Performance Reasoning
        if scores["performance_score"] >= 0.8:
            reasoning["performance_reason"] = f"{agent_name} executed efficiently with fast response time, indicating good optimization."
        elif scores["performance_score"] >= 0.6:
            reasoning["performance_reason"] = f"{agent_name} executed within acceptable time limits with reasonable performance."
        else:
            reasoning["performance_reason"] = f"{agent_name} executed slowly, indicating potential optimization needs."
        
        # Accuracy Reasoning
        if scores["accuracy_score"] >= 0.8:
            reasoning["accuracy_reason"] = f"{agent_name} demonstrated high confidence and successful execution, indicating accurate processing."
        elif scores["accuracy_score"] >= 0.6:
            reasoning["accuracy_reason"] = f"{agent_name} showed moderate confidence with mostly successful execution."
        else:
            reasoning["accuracy_reason"] = f"{agent_name} showed low confidence or failed execution, indicating accuracy issues."
        
        # Relevance Reasoning
        if scores["relevance_score"] >= 0.8:
            reasoning["relevance_reason"] = f"{agent_name} provided highly relevant response that directly addressed the user's input."
        elif scores["relevance_score"] >= 0.6:
            reasoning["relevance_reason"] = f"{agent_name} provided a reasonably relevant response with some connection to the input."
        else:
            reasoning["relevance_reason"] = f"{agent_name} provided a response that may not fully address the user's input or context."
        
        # User Experience Reasoning
        if scores["user_experience_score"] >= 0.8:
            reasoning["user_experience_reason"] = f"{agent_name} provided an excellent user experience with helpful, complete, and engaging response."
        elif scores["user_experience_score"] >= 0.6:
            reasoning["user_experience_reason"] = f"{agent_name} provided a good user experience with adequate helpfulness and completeness."
        else:
            reasoning["user_experience_reason"] = f"{agent_name} provided a basic user experience that could be more helpful or engaging."
        
        # Overall Reasoning
        if scores["overall_score"] >= 0.8:
            reasoning["overall_reason"] = f"{agent_name} performed excellently across all evaluation criteria, providing high-quality service."
        elif scores["overall_score"] >= 0.6:
            reasoning["overall_reason"] = f"{agent_name} performed well overall with good quality and user experience."
        else:
            reasoning["overall_reason"] = f"{agent_name} needs improvement in multiple areas to provide better service quality."
        
        return reasoning
    
    def _calculate_response_quality_score(self, output_data: Dict, confidence: float) -> float:
        """Calculate response quality score based on output data"""
        score = confidence * 0.5  # Base score from confidence
        
        # Check for structured response
        if isinstance(output_data, dict):
            score += 0.1
            
            # Check for reasoning
            if "reasoning" in output_data and output_data["reasoning"]:
                score += 0.2
            
            # Check for helpful details
            if "response" in output_data and len(str(output_data["response"])) > 50:
                score += 0.1
            
            # Check for additional context
            if any(key in output_data for key in ["context", "details", "explanation"]):
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_performance_score(self, execution_time: float, agent_name: str) -> float:
        """Calculate performance score based on execution time"""
        # Different agents have different expected execution times
        expected_times = {
            "ConversationAgent": 2.0,
            "EvaluationAgent": 3.0,
            "VocabularyBuilder": 1.5,
            "PronunciationCoach": 2.5,
            "CulturalEtiquette": 2.0,
            "MotivationCoach": 1.8
        }
        
        expected_time = expected_times.get(agent_name, 2.0)
        
        if execution_time <= expected_time:
            return 1.0
        elif execution_time <= expected_time * 1.5:
            return 0.8
        elif execution_time <= expected_time * 2.0:
            return 0.6
        else:
            return max(0.2, 1.0 - (execution_time / expected_time))
    
    def _calculate_accuracy_score(self, confidence: float, status: str) -> float:
        """Calculate accuracy score based on confidence and status"""
        if status == "success":
            return confidence
        else:
            return confidence * 0.3  # Penalize failed executions
    
    def _calculate_relevance_score(self, input_data: Dict, output_data: Dict) -> float:
        """Calculate relevance score based on input-output relationship"""
        score = 0.5  # Base score
        
        # Check if output addresses input
        if "user_question" in input_data and "response" in output_data:
            input_text = str(input_data["user_question"]).lower()
            output_text = str(output_data["response"]).lower()
            
            # Simple keyword matching
            input_words = set(input_text.split())
            output_words = set(output_text.split())
            
            if input_words and output_words:
                overlap = len(input_words.intersection(output_words))
                score += min(0.3, overlap / len(input_words))
        
        return min(score, 1.0)
    
    def _calculate_user_experience_score(self, output_data: Dict, input_data: Dict) -> float:
        """Calculate user experience score based on helpfulness and completeness"""
        score = 0.5  # Base score
        
        if isinstance(output_data, dict):
            # Check for helpful response
            if "response" in output_data:
                response = str(output_data["response"])
                if len(response) > 100:  # Substantial response
                    score += 0.2
                if any(word in response.lower() for word in ["help", "assist", "suggest", "recommend"]):
                    score += 0.1
            
            # Check for additional helpful information
            if any(key in output_data for key in ["suggestions", "recommendations", "tips", "advice"]):
                score += 0.2
        
        return min(score, 1.0)
    
    def _log_to_arize(self, metrics: AgentEvaluationMetrics, input_data: Dict, output_data: Dict):
        """Log metrics to Arize platform"""
        try:
            # Prepare features for Arize
            features = {
                "agent_name": metrics.agent_name,
                "user_id": metrics.user_id,
                "session_id": metrics.session_id,
                "input_tokens": metrics.input_tokens,
                "output_tokens": metrics.output_tokens,
                "execution_time_ms": metrics.execution_time_ms,
                "confidence_score": metrics.confidence_score,
                "success_rate": metrics.success_rate,
                "response_quality_score": metrics.response_quality_score,
                "error_rate": metrics.error_rate,
                "retry_count": metrics.retry_count,
                **metrics.metadata
            }
            
            # Log to Arize
            self.client.log(
                model_id=f"{metrics.agent_name}_performance",
                model_version="1.0",
                model_type=ModelTypes.REGRESSION,
                environment=Environments.PRODUCTION if self.environment == "production" else Environments.TRAINING,
                prediction_id=f"{metrics.user_id}_{metrics.session_id}_{int(time.time())}",
                features=features,
                prediction_label=metrics.confidence_score,
                actual_label=metrics.response_quality_score,
                tags={
                    "agent": metrics.agent_name,
                    "user_id": metrics.user_id,
                    "environment": self.environment
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log metrics to Arize: {str(e)}")
    
    def _create_trace_span(self, agent_name: str, input_data: Dict, output_data: Dict, 
                          execution_time: float, status: str):
        """Create OpenTelemetry trace span for agent execution"""
        if not self.tracer:
            return
        
        try:
            with self.tracer.start_as_current_span(f"{agent_name}_execution") as span:
                # Set span attributes with proper OpenTelemetry conventions
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.execution_time_ms", execution_time * 1000)
                span.set_attribute("agent.status", status)
                span.set_attribute("agent.input_size", len(str(input_data)))
                span.set_attribute("agent.output_size", len(str(output_data)))
                
                # Add agent metadata for proper visualization
                span.set_attribute("graph.node.id", agent_name)
                span.set_attribute("graph.node.display_name", agent_name.replace("_", " ").title())
                
                # Add input/output data for visibility
                if input_data:
                    span.set_attribute("input.user_question", str(input_data.get("user_question", "")))
                    span.set_attribute("input.context", str(input_data.get("context", "")))
                
                if output_data:
                    span.set_attribute("output.response", str(output_data.get("response", "")))
                    span.set_attribute("output.confidence", float(output_data.get("confidence", 0.0)))
                    span.set_attribute("output.reasoning", str(output_data.get("reasoning", "")))
                
                # Set span status
                if status == "success":
                    span.set_status(Status(StatusCode.OK))
                else:
                    span.set_status(Status(StatusCode.ERROR, "Agent execution failed"))
                
                # Add events
                span.add_event("agent_start", {"timestamp": time.time()})
                span.add_event("agent_complete", {
                    "timestamp": time.time(),
                    "execution_time": execution_time
                })
                
        except Exception as e:
            logger.error(f"Failed to create trace span: {str(e)}")
    
    def _count_tokens(self, data: Dict[str, Any]) -> int:
        """Estimate token count for input/output data"""
        try:
            text = json.dumps(data)
            # Rough estimation: 1 token ≈ 4 characters
            return len(text) // 4
        except:
            return 0
    
    def _calculate_quality_score(self, output_data: Dict[str, Any]) -> float:
        """Calculate response quality score based on output data"""
        try:
            score = 0.5  # Base score
            
            # Check for structured response
            if isinstance(output_data, dict):
                score += 0.1
                
                # Check for confidence in response
                if "confidence" in output_data:
                    score += min(output_data["confidence"] * 0.3, 0.3)
                
                # Check for reasoning
                if "reasoning" in output_data and output_data["reasoning"]:
                    score += 0.1
            
            return min(score, 1.0)
        except:
            return 0.5
    
    def get_agent_performance_summary(self, agent_name: str, days: int = 7) -> Dict[str, Any]:
        """
        Get performance summary for an agent from Arize
        """
        if not self.enabled:
            return {"error": "Arize not enabled"}
        
        try:
            # This would typically involve querying Arize's API
            # For now, return a placeholder structure
            return {
                "agent_name": agent_name,
                "period_days": days,
                "total_executions": 0,
                "average_confidence": 0.0,
                "average_execution_time_ms": 0.0,
                "success_rate": 0.0,
                "error_rate": 0.0,
                "quality_trend": "stable"
            }
        except Exception as e:
            logger.error(f"Failed to get performance summary: {str(e)}")
            return {"error": str(e)}
    
    def create_evaluation_task(self, 
                             task_name: str,
                             agent_name: str,
                             evaluation_criteria: Dict[str, Any],
                             schedule: str = "continuous"):
        """
        Create an evaluation task in Arize dashboard
        """
        if not self.enabled:
            logger.warning("Cannot create evaluation task: Arize not enabled")
            return
        
        try:
            # This would create evaluation tasks in Arize
            # For now, log the task configuration
            task_config = {
                "task_name": task_name,
                "agent_name": agent_name,
                "evaluation_criteria": evaluation_criteria,
                "schedule": schedule,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Created evaluation task: {task_name} for {agent_name}")
            logger.debug(f"Task configuration: {json.dumps(task_config, indent=2)}")
            
        except Exception as e:
            logger.error(f"Failed to create evaluation task: {str(e)}")

# Global instance
arize_integration = ArizeIntegration()

# Convenience functions
def log_agent_execution(agent_name: str, user_id: str, session_id: str, 
                       input_data: Dict, output_data: Dict, execution_time: float,
                       confidence: float, status: str = "success", **kwargs):
    """Convenience function to log agent execution"""
    arize_integration.log_agent_execution(
        agent_name, user_id, session_id, input_data, output_data,
        execution_time, confidence, status, **kwargs
    )

def log_evaluation_result(agent_name: str, user_id: str, evaluation_type: str,
                         evaluation_data: Dict, score: float, **kwargs):
    """Convenience function to log evaluation results"""
    arize_integration.log_evaluation_result(
        agent_name, user_id, evaluation_type, evaluation_data, score, **kwargs
    )

def log_user_interaction(user_id: str, interaction_type: str, 
                        interaction_data: Dict, **kwargs):
    """Convenience function to log user interactions"""
    arize_integration.log_user_interaction(
        user_id, interaction_type, interaction_data, **kwargs
    )

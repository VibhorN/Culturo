"""
Arize Phoenix Tracing Integration for Agent Evaluations
Uses Phoenix OTEL for LLM traces as recommended by Arize
Based on: https://arize.com/docs/phoenix/tracing/how-to-tracing/setup-tracing
"""

import os
import logging
from typing import Dict, Any, Optional

# Ensure environment is loaded
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Check if Phoenix is available
try:
    from phoenix.otel import register
    PHOENIX_AVAILABLE = True
except ImportError:
    PHOENIX_AVAILABLE = False
    logger.warning("Phoenix OTEL not installed. Install with: pip install arize-phoenix-otel")

tracer_provider = None

def initialize_phoenix_tracing():
    """
    Initialize Phoenix OTEL tracing for LLM calls
    This should be called BEFORE any LLM code execution
    """
    global tracer_provider
    
    if not PHOENIX_AVAILABLE:
        logger.warning("Phoenix OTEL not available. Skipping Phoenix tracing.")
        return None
    
    try:
        # Get credentials from environment
        phoenix_api_key = os.getenv("PHOENIX_API_KEY")
        phoenix_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
        project_name = os.getenv("PHOENIX_PROJECT_NAME", "lingua-cal-agent-evaluations")
        
        if not phoenix_api_key or not phoenix_endpoint:
            logger.warning("Phoenix credentials not found. Set PHOENIX_API_KEY and PHOENIX_COLLECTOR_ENDPOINT")
            return None
        
        logger.info(f"Initializing Phoenix tracing for project: {project_name}")
        
        # Configure Phoenix tracer with auto-instrumentation
        tracer_provider = register(
            project_name=project_name,
            endpoint=phoenix_endpoint,
            auto_instrument=True,  # Automatically instrument LLM calls
        )
        
        logger.info("✅ Phoenix OTEL tracing initialized successfully")
        logger.info("   Phoenix will automatically trace Anthropic/LLM calls")
        
        return tracer_provider
        
    except Exception as e:
        logger.error(f"Failed to initialize Phoenix tracing: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_tracer():
    """Get the OpenTelemetry tracer for manual spans"""
    if tracer_provider:
        from opentelemetry import trace
        return tracer_provider.get_tracer(__name__)
    return None


async def log_agent_evaluation(user_id: str, question: str, response: str, agents_used: Dict, anthropic_client=None):
    """
    Log agent evaluation to Phoenix with structured data
    Creates ONE row with: question, response, and for each agent: score, reasoning, and thought process
    Also evaluates if the response adequately answers the question
    """
    tracer = get_tracer()
    
    if not tracer:
        logger.warning("Phoenix tracer not available")
        return
    
    try:
        # Evaluate each agent using Anthropic
        agent_scores = {}
        for agent_name, agent_data in agents_used.items():
            score, reasoning = await evaluate_agent_with_anthropic(
                anthropic_client, agent_name, question, agent_data
            )
            agent_scores[agent_name] = {"score": score, "reasoning": reasoning}
        
        # Evaluate if the overall response adequately answers the question
        overall_eval = await evaluate_response_adequacy(anthropic_client, question, response)
        
        # Create a single span with all the structured data
        with tracer.start_as_current_span("agent_evaluation") as span:
            # Core columns
            span.set_attribute("user_id", user_id)
            span.set_attribute("question", question)
            span.set_attribute("response", response)
            span.set_attribute("total_agents_used", len(agents_used))
            
            # Overall response evaluation
            span.set_attribute("response_adequacy_score", overall_eval.get("score", 0.5))
            span.set_attribute("response_adequacy_reasoning", overall_eval.get("reasoning", "Evaluation not available"))
            
            # For each agent, add score, reasoning, and thought process
            for agent_name, agent_data in agents_used.items():
                eval_data = agent_scores.get(agent_name, {"score": 0.5, "reasoning": "Evaluation not available"})
                
                # Agent score column
                span.set_attribute(f"{agent_name}_score", eval_data["score"])
                # Agent reasoning column (evaluator's reasoning)
                span.set_attribute(f"{agent_name}_reasoning", eval_data["reasoning"])
                
                # Agent thought process (the LLM's own reasoning)
                thought_process = agent_data.get("thought_process", agent_data.get("reasoning", ""))
                span.set_attribute(f"{agent_name}_thought_process", thought_process)
                
                # Also add metadata
                span.set_attribute(f"{agent_name}_status", agent_data.get("status", "unknown"))
                span.set_attribute(f"{agent_name}_execution_time_s", agent_data.get("execution_time", 0.0))
            
            logger.info(f"✅ Logged structured agent evaluation to Phoenix for user {user_id}")
            logger.info(f"   Agents evaluated: {list(agents_used.keys())}")
            logger.info(f"   Overall response adequacy score: {overall_eval.get('score', 0.5)}")
            
    except Exception as e:
        logger.error(f"Failed to log to Phoenix: {str(e)}")
        import traceback
        traceback.print_exc()


async def evaluate_agent_with_anthropic(anthropic_client, agent_name: str, question: str, agent_data: Dict):
    """
    Evaluate an agent's performance using Anthropic Claude
    Returns (score, reasoning) tuple
    """
    if not anthropic_client:
        return 0.5, "Anthropic client not available for evaluation"
    
    try:
        prompt = f"""You are an AI agent evaluator. Evaluate the performance of this agent:

Agent Name: {agent_name}
User Question: "{question}"
Agent Output: {agent_data.get('output_data', {})}
Agent Status: {agent_data.get('status', 'unknown')}
Agent Confidence: {agent_data.get('confidence', 0.0)}

Evaluate based on:
1. Relevance: How well did the agent address the question?
2. Quality: Is the output clear and useful?
3. Accuracy: Is the information correct?

Provide:
- Score: A number between 0.0 and 1.0
- Reasoning: A brief explanation (1-2 sentences)

Respond in JSON format:
{{
    "score": 0.85,
    "reasoning": "Brief explanation of the evaluation"
}}"""

        # Use Anthropic Messages API
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text
        import json
        import re
        
        # Parse JSON from response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result_text, re.DOTALL)
        if json_match:
            evaluation = json.loads(json_match.group())
            return evaluation.get("score", 0.5), evaluation.get("reasoning", "No reasoning provided")
        else:
            return 0.5, "Failed to parse evaluation response"
            
    except Exception as e:
        logger.error(f"Failed to evaluate agent {agent_name}: {str(e)}")
        return 0.5, f"Evaluation error: {str(e)}"


async def evaluate_response_adequacy(anthropic_client, question: str, response: str):
    """
    Evaluate if the overall response adequately answers the user's question
    Returns dict with score and reasoning
    """
    if not anthropic_client:
        return {"score": 0.5, "reasoning": "Anthropic client not available for evaluation"}
    
    try:
        prompt = f"""You are an AI response evaluator. Evaluate if the response adequately answers the user's question.

User Question: "{question}"
Response: "{response}"

Evaluate based on:
1. Does the response directly address the question?
2. Is the response comprehensive enough to satisfy the user's intent?
3. Does the response provide useful, relevant information?

Provide:
- Score: A number between 0.0 and 1.0 (1.0 = perfectly answers the question, 0.0 = completely off-topic)
- Reasoning: A brief explanation (1-2 sentences) of why the response is or isn't adequate

Respond in JSON format:
{{
    "score": 0.85,
    "reasoning": "Brief explanation of the evaluation"
}}"""

        # Use Anthropic Messages API
        api_response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = api_response.content[0].text
        import json
        import re
        
        # Parse JSON from response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result_text, re.DOTALL)
        if json_match:
            evaluation = json.loads(json_match.group())
            return evaluation
        else:
            return {"score": 0.5, "reasoning": "Failed to parse evaluation response"}
            
    except Exception as e:
        logger.error(f"Failed to evaluate response adequacy: {str(e)}")
        return {"score": 0.5, "reasoning": f"Evaluation error: {str(e)}"}


# Initialize Phoenix tracing on module import
# This must happen BEFORE any LLM calls are made
if PHOENIX_AVAILABLE:
    initialize_phoenix_tracing()


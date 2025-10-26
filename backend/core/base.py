"""
Base Agent Class
Common functionality for all agents
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Import logging system
try:
    from utils.logging import AgentLogger
    agent_logger = AgentLogger()
except ImportError:
    # Fallback if logging system not available
    agent_logger = None

# Import Arize integration
try:
    from integrations.arize import arize_integration, log_agent_execution
    ARIZE_AVAILABLE = True
except ImportError:
    ARIZE_AVAILABLE = False


@dataclass
class AgentMessage:
    """Message passed between agents"""
    sender: str
    recipient: str
    content: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Standardized agent response"""
    agent_name: str
    status: str  # success, error, pending
    data: Any
    confidence: float = 0.0
    reasoning: str = ""
    next_actions: List[str] = field(default_factory=list)


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str, anthropic_api_key: str):
        self.name = name
        self.anthropic_api_key = anthropic_api_key
        self.message_history: List[AgentMessage] = []
        logger.info(f"Initialized agent: {name}")
    
    async def process(self, input_data: Dict) -> AgentResponse:
        """Process input and return response with automatic logging"""
        start_time = time.time()
        user_id = input_data.get("user_id", "anonymous")
        session_id = input_data.get("session_id", f"session_{int(time.time())}")
        
        try:
            # Call the actual process method
            result = await self._process_impl(input_data)
            
            # Log the reasoning
            execution_time = time.time() - start_time
            if agent_logger:
                agent_logger.log_agent_reasoning(
                    agent_name=self.name,
                    operation="process",
                    input_data=input_data,
                    output_data=result.data if hasattr(result, 'data') else {},
                    reasoning=result.reasoning if hasattr(result, 'reasoning') else "",
                    confidence=result.confidence if hasattr(result, 'confidence') else 0.0,
                    execution_time=execution_time
                )
                
                # Log performance
                agent_logger.log_performance(
                    operation=f"{self.name}_process",
                    duration=execution_time,
                    metadata={
                        "agent_name": self.name,
                        "status": result.status if hasattr(result, 'status') else "unknown",
                        "confidence": result.confidence if hasattr(result, 'confidence') else 0.0
                    }
                )
            
            # Log to Arize for comprehensive evaluation and monitoring
            if ARIZE_AVAILABLE:
                arize_integration.log_comprehensive_agent_evaluation(
                    agent_name=self.name,
                    user_id=user_id,
                    session_id=session_id,
                    input_data=input_data,
                    output_data=result.data if hasattr(result, 'data') else {},
                    execution_time=execution_time,
                    confidence=result.confidence if hasattr(result, 'confidence') else 0.0,
                    status=result.status if hasattr(result, 'status') else "success",
                    metadata={
                        "reasoning": result.reasoning if hasattr(result, 'reasoning') else "",
                        "next_actions": result.next_actions if hasattr(result, 'next_actions') else []
                    }
                )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            user_id = input_data.get("user_id", "anonymous")
            session_id = input_data.get("session_id", f"session_{int(time.time())}")
            
            # Log error
            if agent_logger:
                agent_logger.log_agent_reasoning(
                    agent_name=self.name,
                    operation="process_error",
                    input_data=input_data,
                    output_data={"error": str(e)},
                    reasoning=f"Error occurred: {str(e)}",
                    confidence=0.0,
                    execution_time=execution_time
                )
                
                # Log performance for error case
                agent_logger.log_performance(
                    operation=f"{self.name}_process_error",
                    duration=execution_time,
                    metadata={
                        "agent_name": self.name,
                        "error": str(e)
                    }
                )
            
            # Log error to Arize for monitoring
            if ARIZE_AVAILABLE:
                log_agent_execution(
                    agent_name=self.name,
                    user_id=user_id,
                    session_id=session_id,
                    input_data=input_data,
                    output_data={"error": str(e)},
                    execution_time=execution_time,
                    confidence=0.0,
                    status="error",
                    error_message=str(e),
                    metadata={"error_type": type(e).__name__}
                )
            
            raise
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """Actual process implementation - to be overridden by subclasses"""
        raise NotImplementedError("Agents must implement _process_impl method")
    
    def log_message(self, message: AgentMessage):
        """Log agent messages for tracing"""
        self.message_history.append(message)
        logger.info(f"[{self.name}] {message.sender} -> {message.recipient}: {message.content}")

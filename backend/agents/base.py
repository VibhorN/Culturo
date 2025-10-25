"""
Base Agent Class
Common functionality for all agents
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


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
        """Process input and return response"""
        raise NotImplementedError("Agents must implement process method")
    
    def log_message(self, message: AgentMessage):
        """Log agent messages for tracing"""
        self.message_history.append(message)
        logger.info(f"[{self.name}] {message.sender} -> {message.recipient}: {message.content}")

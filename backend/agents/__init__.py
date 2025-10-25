"""
Agent System for WorldWise
Import all agents from the agents module
"""

from core.orchestrator import AgentOrchestrator
from .data_retrieval import DataRetrievalAgent

# Export the main orchestrator and data retrieval agent for easy importing
__all__ = ['AgentOrchestrator', 'DataRetrievalAgent']

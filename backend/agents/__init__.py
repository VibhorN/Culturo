"""
Agent System for WorldWise
Import all agents from the agents module
"""

from .orchestrator_main import AgentOrchestrator

# Export the main orchestrator for easy importing
__all__ = ['AgentOrchestrator']

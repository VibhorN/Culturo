"""
Agent Orchestrator
Coordinates all agents and manages the workflow
"""

import logging
import asyncio
from typing import Dict, List
from .base import AgentResponse
from .orchestrator import OrchestratorAgent
from .language_correction import LanguageCorrectionAgent
from .cultural_context import CulturalContextAgent
from .translation import TranslationAgent
from .conversation import ConversationAgent
from .evaluation import EvaluationAgent
from .personalization import PersonalizationAgent
from .data_retrieval import DataRetrievalAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Main orchestrator that coordinates all agents
    """
    
    def __init__(self, anthropic_api_key: str):
        self.orchestrator = OrchestratorAgent(anthropic_api_key)
        self.language_correction = LanguageCorrectionAgent(anthropic_api_key)
        self.cultural_context = CulturalContextAgent(anthropic_api_key)
        self.translation = TranslationAgent(anthropic_api_key)
        self.conversation = ConversationAgent(anthropic_api_key)
        self.evaluation = EvaluationAgent(anthropic_api_key)
        self.personalization = PersonalizationAgent()
        self.data_retrieval = DataRetrievalAgent(anthropic_api_key)
        logger.info("AgentOrchestrator initialized with all agents using Anthropic API")
    
    async def process_input(self, user_input: Dict) -> Dict:
        """
        Main entry point for processing user input
        """
        try:
            user_id = user_input.get("user_id", "anonymous")
            logger.info(f"[AgentOrchestrator] Processing input from user {user_id}")
            
            # Step 1: Orchestrator analyzes intent and creates plan
            orchestrator_response = await self.orchestrator.process(user_input)
            execution_plan = orchestrator_response.data
            
            # Step 2: Execute agents based on plan
            agent_responses = {}
            agents_activated = []
            
            # Language Correction (if needed)
            if "language_correction" in execution_plan.get("agents_to_activate", []):
                if "text" in user_input:
                    correction_input = {
                        "text": user_input["text"],
                        "target_language": user_input.get("language", "en"),
                        "native_language": user_input.get("native_language", "en"),
                        "audio_confidence": user_input.get("audio_confidence", 1.0)
                    }
                    correction_response = await self.language_correction.process(correction_input)
                    agent_responses["language_correction"] = correction_response
                    agents_activated.append("language_correction")
            
            # Data Retrieval (only if needed)
            if "data_retrieval" in execution_plan.get("agents_to_activate", []):
                target_country = execution_plan.get("target_country", "unknown")
                if target_country and target_country != "none" and target_country != "unknown":
                    data_input = {
                        "country": target_country,
                        "query": user_input.get("query", ""),
                        "context": execution_plan
                    }
                    data_response = await self.data_retrieval.process(data_input)
                    
                    # Check if clarification is needed
                    if data_response.status == "clarification_needed":
                        return {
                            "status": "clarification_needed",
                            "response": data_response.data.get("clarification_question", "Could you clarify what you're looking for?"),
                            "metadata": {
                                "suggested_options": data_response.data.get("suggested_options", []),
                                "agents_activated": ["orchestrator", "data_retrieval"],
                                "execution_plan": execution_plan
                            }
                        }
                    
                    agent_responses["data_retrieval"] = data_response
                    agents_activated.append("data_retrieval")
            
            # Translation (if needed)
            if "translation" in execution_plan.get("agents_to_activate", []):
                translation_input = {
                    "text": user_input.get("text", ""),
                    "source_language": user_input.get("source_language", "en"),
                    "target_language": user_input.get("target_language", "en"),
                    "context": execution_plan
                }
                translation_response = await self.translation.process(translation_input)
                agent_responses["translation"] = translation_response
                agents_activated.append("translation")
            
            # Conversation (always activated)
            conversation_input = {
                "query": user_input.get("query", ""),
                "context": execution_plan,
                "retrieved_data": agent_responses.get("data_retrieval", AgentResponse("", "", {})).data if "data_retrieval" in agent_responses else {},
                "language_corrections": agent_responses.get("language_correction", AgentResponse("", "", {})).data if "language_correction" in agent_responses else {},
                "has_retrieved_data": "data_retrieval" in agent_responses
            }
            conversation_response = await self.conversation.process(conversation_input)
            agent_responses["conversation"] = conversation_response
            agents_activated.append("conversation")
            
            # Evaluation
            evaluation_input = {
                "interaction_data": {
                    "query": user_input.get("query", ""),
                    "country": execution_plan.get("target_country", "unknown"),
                    "language": user_input.get("language", "en"),
                    "timestamp": "now"
                },
                "user_profile": self.personalization.get_profile(user_id),
                "session_context": execution_plan
            }
            evaluation_response = await self.evaluation.process(evaluation_input)
            agent_responses["evaluation"] = evaluation_response
            agents_activated.append("evaluation")
            
            # Personalization
            personalization_input = {
                "user_id": user_id,
                "interaction_data": evaluation_input["interaction_data"],
                "preferences": {}
            }
            personalization_response = await self.personalization.process(personalization_input)
            agent_responses["personalization"] = personalization_response
            agents_activated.append("personalization")
            
            # Compile final response
            final_response = {
                "status": "success",
                "response": conversation_response.data.get("response", "I'm here to help!"),
                "metadata": {
                    "agents_activated": agents_activated,
                    "execution_plan": execution_plan,
                    "agent_responses": {k: v.data for k, v in agent_responses.items()},
                    "confidence": conversation_response.confidence
                }
            }
            
            logger.info(f"[AgentOrchestrator] Completed in {0.82}s")
            return final_response
            
        except Exception as e:
            logger.error(f"[AgentOrchestrator] Error: {str(e)}")
            return {
                "status": "error",
                "response": "I apologize, but I encountered an error. Please try again.",
                "metadata": {
                    "error": str(e),
                    "agents_activated": []
                }
            }

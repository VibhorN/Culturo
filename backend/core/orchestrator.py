"""
Agent Orchestrator
Coordinates all agents and manages the workflow
"""

import logging
import asyncio
from typing import Dict, List
from datetime import datetime
from .base import AgentResponse
from agents.orchestrator import OrchestratorAgent
from agents.language import LanguageCorrectionAgent
from agents.cultural import CulturalContextAgent
from agents.translation import TranslationAgent
from agents.conversation import ConversationAgent
from agents.evaluation import EvaluationAgent
from agents.personalization import PersonalizationAgent
from agents.data_retrieval import DataRetrievalAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Main orchestrator that coordinates all agents
    """
    
    def __init__(self, anthropic_api_key: str, news_api_key: str = None, spotify_client_id: str = None, spotify_client_secret: str = None, tripadvisor_api_key: str = None):
        self.orchestrator = OrchestratorAgent(anthropic_api_key)
        self.language_correction = LanguageCorrectionAgent(anthropic_api_key)
        self.cultural_context = CulturalContextAgent(anthropic_api_key)
        self.translation = TranslationAgent(anthropic_api_key)
        self.conversation = ConversationAgent(anthropic_api_key)
        self.evaluation = EvaluationAgent(anthropic_api_key)
        self.personalization = PersonalizationAgent()
        self.data_retrieval = DataRetrievalAgent(
            anthropic_api_key, 
            news_api_key, 
            spotify_client_id, 
            spotify_client_secret, 
            tripadvisor_api_key
        )
        # Conversation context storage
        self.conversation_context = {}
        logger.info("AgentOrchestrator initialized with all agents using Anthropic API")
    
    def _get_user_context(self, user_id: str) -> Dict:
        """Get conversation context for a user"""
        return self.conversation_context.get(user_id, {
            "last_country": None,
            "conversation_history": [],
            "user_interests": []
        })
    
    def _update_user_context(self, user_id: str, execution_plan: Dict, response: str):
        """Update conversation context for a user"""
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = {
                "last_country": None,
                "conversation_history": [],
                "user_interests": []
            }
        
        # Update last country if specified
        target_country = execution_plan.get("target_country")
        if target_country and target_country not in ["unknown", "none", None]:
            self.conversation_context[user_id]["last_country"] = target_country
        
        # Add to conversation history
        self.conversation_context[user_id]["conversation_history"].append({
            "query": execution_plan.get("intent", "unknown"),
            "country": target_country,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 conversations
        if len(self.conversation_context[user_id]["conversation_history"]) > 10:
            self.conversation_context[user_id]["conversation_history"] = self.conversation_context[user_id]["conversation_history"][-10:]
    
    async def process_input(self, user_input: Dict) -> Dict:
        """
        Main entry point for processing user input
        """
        try:
            user_id = user_input.get("user_id", "anonymous")
            logger.info(f"[AgentOrchestrator] Processing input from user {user_id}")
            
            # Get conversation context for this user
            user_context = self._get_user_context(user_id)
            
            # Enhance user input with conversation context
            enhanced_input = user_input.copy()
            enhanced_input["context"] = {
                "last_country": user_context["last_country"],
                "conversation_history": user_context["conversation_history"][-3:],  # Last 3 conversations
                "user_interests": user_context["user_interests"]
            }
            
            # Step 1: Orchestrator analyzes intent and creates plan
            orchestrator_response = await self.orchestrator.process(enhanced_input)
            execution_plan = orchestrator_response.data
            
            # Check if orchestrator needs clarification
            if execution_plan.get("needs_clarification", False):
                return {
                    "status": "clarification_needed",
                    "response": execution_plan.get("clarifying_question", "Could you clarify what you're looking for?"),
                    "metadata": {
                        "agents_activated": ["orchestrator"],
                        "execution_plan": execution_plan,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
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
                # Allow data retrieval for global queries (news, general topics) even without specific country
                data_sources = execution_plan.get("data_sources", [])
                is_global_query = not target_country or target_country in ["none", "unknown", None] and "news" in data_sources
                
                if target_country and target_country not in ["none", "unknown", None] or is_global_query:
                    data_input = {
                        "country": target_country or "global",
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
                    "agent_responses": {k: {
                        "status": v.status,
                        "data": v.data,
                        "confidence": v.confidence,
                        "reasoning": v.reasoning,
                        "agent_name": v.agent_name
                    } for k, v in agent_responses.items()},
                    "confidence": conversation_response.confidence
                }
            }
            
            # Update conversation context
            self._update_user_context(user_id, execution_plan, final_response["response"])
            
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

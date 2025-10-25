"""
Personalization Agent
Tracks user preferences and adapts the experience
"""

import json
import logging
from typing import Dict
from core.base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


class PersonalizationAgent(BaseAgent):
    """
    Tracks user preferences and adapts the experience
    """
    
    def __init__(self):
        super().__init__("Personalization", "")
        self.user_profiles = {}
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Updates user profile and provides personalization
        """
        try:
            user_id = input_data.get("user_id", "anonymous")
            interaction_data = input_data.get("interaction_data", {})
            preferences = input_data.get("preferences", {})
            
            logger.info(f"[Personalization] Updated profile for user {user_id}")
            
            # Update user profile
            profile = self._update_profile(user_id, interaction_data, preferences)
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data=profile,
                confidence=0.9,
                reasoning="Profile updated successfully"
            )
            
        except Exception as e:
            logger.error(f"[Personalization] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    def _update_profile(self, user_id: str, interaction: Dict, preferences: Dict) -> Dict:
        """Update user profile based on interaction"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "interests": [],
                "learning_goals": [],
                "preferred_languages": [],
                "cultural_focus": [],
                "interaction_count": 0,
                "last_interaction": None
            }
        
        profile = self.user_profiles[user_id]
        profile["interaction_count"] += 1
        profile["last_interaction"] = interaction.get("timestamp", "unknown")
        
        # Update interests based on interaction
        if "country" in interaction:
            if interaction["country"] not in profile["cultural_focus"]:
                profile["cultural_focus"].append(interaction["country"])
        
        if "language" in interaction:
            if interaction["language"] not in profile["preferred_languages"]:
                profile["preferred_languages"].append(interaction["language"])
        
        # Update preferences
        profile.update(preferences)
        
        return profile
    
    def get_profile(self, user_id: str) -> Dict:
        """Get user profile"""
        return self.user_profiles.get(user_id, {})

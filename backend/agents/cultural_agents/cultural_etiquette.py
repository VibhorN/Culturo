"""
Cultural Etiquette Agent
Provides context-specific etiquette guidance and cultural sensitivity training
"""

import json
import logging
import aiohttp
import time
from typing import Dict, List
from ..base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

# Import logging system
try:
    from utils.logging import log_api_call
except ImportError:
    def log_api_call(*args, **kwargs):
        pass


class CulturalEtiquetteAgent(BaseAgent):
    """
    Provides cultural etiquette guidance through:
    - Context-specific etiquette rules
    - Business vs. social customs
    - Cultural taboos and sensitive topics
    - Role-playing scenarios for different situations
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("CulturalEtiquette", anthropic_api_key)
        self.etiquette_database = {}  # Cache for etiquette rules
        self.user_contexts = {}  # Track user's cultural contexts
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Provides cultural etiquette guidance based on context
        """
        try:
            user_id = input_data.get("user_id", "anonymous")
            country = input_data.get("country", "unknown")
            situation = input_data.get("situation", "general")
            context_type = input_data.get("context_type", "social")  # social, business, formal, casual
            user_native_culture = input_data.get("native_culture", "western")
            
            logger.info(f"[CulturalEtiquette] Providing etiquette guidance for {country} - {situation}")
            
            # Get or create etiquette guidance
            etiquette_guidance = await self._get_etiquette_guidance(
                country, situation, context_type, user_native_culture
            )
            
            # Generate role-playing scenarios
            scenarios = await self._generate_scenarios(country, situation, context_type)
            
            # Provide cultural sensitivity tips
            sensitivity_tips = await self._get_sensitivity_tips(country, user_native_culture)
            
            # Update user context tracking
            self._update_user_context(user_id, country, situation, context_type)
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data={
                    "etiquette_guidance": etiquette_guidance,
                    "role_playing_scenarios": scenarios,
                    "sensitivity_tips": sensitivity_tips,
                    "cultural_context": {
                        "country": country,
                        "situation": situation,
                        "context_type": context_type
                    },
                    "user_context_history": self.user_contexts.get(user_id, [])[-5:]  # Last 5 contexts
                },
                confidence=etiquette_guidance.get("confidence", 0.8),
                reasoning=etiquette_guidance.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"[CulturalEtiquette] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _get_etiquette_guidance(self, country: str, situation: str, context_type: str, native_culture: str) -> Dict:
        """Get detailed etiquette guidance for specific cultural context"""
        try:
            cache_key = f"{country}_{situation}_{context_type}"
            if cache_key in self.etiquette_database:
                return self.etiquette_database[cache_key]
            
            prompt = f"""
            You are a cultural etiquette expert. Provide comprehensive etiquette guidance.
            
            Country: {country}
            Situation: {situation}
            Context Type: {context_type} (social/business/formal/casual)
            User's Native Culture: {native_culture}
            
            Provide detailed guidance on:
            1. Greeting customs and introductions
            2. Communication style and body language
            3. Dining etiquette (if applicable)
            4. Gift-giving customs
            5. Business etiquette (if business context)
            6. Social norms and expectations
            7. Common mistakes to avoid
            8. Cultural taboos and sensitive topics
            
            Focus on practical, actionable advice that helps avoid cultural misunderstandings.
            
            Respond in JSON:
            {{
                "greeting_customs": {{
                    "formal": "...",
                    "casual": "...",
                    "business": "...",
                    "body_language": "..."
                }},
                "communication_style": {{
                    "directness": "direct/indirect",
                    "formality": "formal/semi-formal/casual",
                    "eye_contact": "...",
                    "personal_space": "...",
                    "interruption_norms": "..."
                }},
                "dining_etiquette": {{
                    "table_manners": ["rule1", "rule2"],
                    "host_guest_dynamics": "...",
                    "tipping_customs": "...",
                    "food_restrictions": "..."
                }},
                "gift_giving": {{
                    "appropriate_gifts": ["gift1", "gift2"],
                    "inappropriate_gifts": ["gift1", "gift2"],
                    "gift_wrapping": "...",
                    "presentation_timing": "..."
                }},
                "business_etiquette": {{
                    "meeting_protocols": "...",
                    "hierarchy_respect": "...",
                    "decision_making": "...",
                    "follow_up": "..."
                }},
                "social_norms": {{
                    "punctuality": "...",
                    "dress_code": "...",
                    "conversation_topics": {{
                        "appropriate": ["topic1", "topic2"],
                        "avoid": ["topic1", "topic2"]
                    }}
                }},
                "common_mistakes": ["mistake1", "mistake2", "mistake3"],
                "cultural_taboos": ["taboo1", "taboo2"],
                "sensitivity_notes": ["note1", "note2"],
                "confidence": 0.9,
                "reasoning": "..."
            }}
            """
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    execution_time = time.time() - start_time
                    
                    log_api_call(
                        service="anthropic",
                        endpoint="/v1/messages",
                        method="POST",
                        request_data=data,
                        response_data={"status": response.status, "content": "..."},
                        status_code=response.status,
                        execution_time=execution_time
                    )
                    
                    if response.status == 200:
                        result = await response.json()
                        guidance_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = guidance_text.find('{')
            end_idx = guidance_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                try:
                    guidance = json.loads(guidance_text[start_idx:end_idx])
                    # Cache the result
                    self.etiquette_database[cache_key] = guidance
                    return guidance
                except json.JSONDecodeError as json_err:
                    logger.error(f"[CulturalEtiquette] JSON parsing error: {str(json_err)}")
                    logger.debug(f"[CulturalEtiquette] Raw response: {guidance_text[start_idx:end_idx]}")
                    
        except Exception as e:
            logger.error(f"[CulturalEtiquette] Error getting etiquette guidance: {str(e)}")
        
        return {
            "greeting_customs": {"formal": "", "casual": "", "business": "", "body_language": ""},
            "communication_style": {"directness": "unknown", "formality": "unknown", "eye_contact": "", "personal_space": "", "interruption_norms": ""},
            "dining_etiquette": {"table_manners": [], "host_guest_dynamics": "", "tipping_customs": "", "food_restrictions": ""},
            "gift_giving": {"appropriate_gifts": [], "inappropriate_gifts": [], "gift_wrapping": "", "presentation_timing": ""},
            "business_etiquette": {"meeting_protocols": "", "hierarchy_respect": "", "decision_making": "", "follow_up": ""},
            "social_norms": {"punctuality": "", "dress_code": "", "conversation_topics": {"appropriate": [], "avoid": []}},
            "common_mistakes": [],
            "cultural_taboos": [],
            "sensitivity_notes": [],
            "confidence": 0.3,
            "reasoning": "Unable to provide guidance"
        }
    
    async def _generate_scenarios(self, country: str, situation: str, context_type: str) -> List[Dict]:
        """Generate role-playing scenarios for practice"""
        try:
            prompt = f"""
            Create 3-4 realistic role-playing scenarios for practicing cultural etiquette.
            
            Country: {country}
            Situation: {situation}
            Context Type: {context_type}
            
            Each scenario should:
            1. Be realistic and common
            2. Test specific etiquette rules
            3. Include multiple characters
            4. Have clear success/failure outcomes
            5. Provide learning opportunities
            
            Respond in JSON:
            {{
                "scenarios": [
                    {{
                        "id": "scenario_1",
                        "title": "...",
                        "description": "...",
                        "characters": ["character1", "character2"],
                        "setting": "...",
                        "etiquette_focus": ["rule1", "rule2"],
                        "correct_approach": "...",
                        "common_mistakes": ["mistake1", "mistake2"],
                        "practice_tips": ["tip1", "tip2"],
                        "difficulty": "beginner/intermediate/advanced"
                    }}
                ],
                "scenario_instructions": "How to practice these scenarios effectively"
            }}
            """
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        scenarios_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = scenarios_text.find('{')
            end_idx = scenarios_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(scenarios_text[start_idx:end_idx]).get("scenarios", [])
                except json.JSONDecodeError as json_err:
                    logger.error(f"[CulturalEtiquette] JSON parsing error in scenarios: {str(json_err)}")
                    logger.debug(f"[CulturalEtiquette] Raw scenarios response: {scenarios_text[start_idx:end_idx]}")
                    
        except Exception as e:
            logger.error(f"[CulturalEtiquette] Error generating scenarios: {str(e)}")
        
        return []
    
    async def _get_sensitivity_tips(self, country: str, native_culture: str) -> Dict:
        """Get cultural sensitivity tips and awareness guidance"""
        try:
            prompt = f"""
            Provide cultural sensitivity tips for someone from {native_culture} culture interacting with {country} culture.
            
            Focus on:
            1. Common cultural misunderstandings
            2. Historical context awareness
            3. Religious and spiritual considerations
            4. Social justice and equality issues
            5. Language sensitivity
            6. Non-verbal communication differences
            
            Respond in JSON:
            {{
                "cultural_misunderstandings": [
                    {{
                        "misunderstanding": "...",
                        "explanation": "...",
                        "how_to_avoid": "..."
                    }}
                ],
                "historical_context": [
                    {{
                        "event": "...",
                        "cultural_impact": "...",
                        "sensitivity_considerations": "..."
                    }}
                ],
                "religious_considerations": [
                    {{
                        "practice": "...",
                        "respectful_approach": "...",
                        "common_mistakes": "..."
                    }}
                ],
                "language_sensitivity": [
                    {{
                        "phrase": "...",
                        "cultural_meaning": "...",
                        "appropriate_usage": "..."
                    }}
                ],
                "non_verbal_differences": [
                    {{
                        "gesture": "...",
                        "meaning_in_target": "...",
                        "meaning_in_native": "...",
                        "advice": "..."
                    }}
                ],
                "general_principles": ["principle1", "principle2", "principle3"]
            }}
            """
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1200,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        tips_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = tips_text.find('{')
            end_idx = tips_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(tips_text[start_idx:end_idx])
                    
        except Exception as e:
            logger.error(f"[CulturalEtiquette] Error getting sensitivity tips: {str(e)}")
        
        return {
            "cultural_misunderstandings": [],
            "historical_context": [],
            "religious_considerations": [],
            "language_sensitivity": [],
            "non_verbal_differences": [],
            "general_principles": []
        }
    
    def _update_user_context(self, user_id: str, country: str, situation: str, context_type: str):
        """Update user's cultural context history"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = []
        
        context_entry = {
            "country": country,
            "situation": situation,
            "context_type": context_type,
            "timestamp": time.time()
        }
        
        self.user_contexts[user_id].append(context_entry)
        
        # Keep only last 20 contexts
        if len(self.user_contexts[user_id]) > 20:
            self.user_contexts[user_id] = self.user_contexts[user_id][-20:]
    
    def get_user_cultural_profile(self, user_id: str) -> Dict:
        """Get user's cultural interaction profile"""
        if user_id not in self.user_contexts:
            return {"status": "new_user", "message": "No cultural interactions yet"}
        
        contexts = self.user_contexts[user_id]
        
        # Analyze cultural preferences
        countries_visited = list(set([ctx["country"] for ctx in contexts]))
        context_types = list(set([ctx["context_type"] for ctx in contexts]))
        situations = list(set([ctx["situation"] for ctx in contexts]))
        
        return {
            "total_interactions": len(contexts),
            "countries_explored": countries_visited,
            "context_types_used": context_types,
            "situations_practiced": situations,
            "most_common_country": max(set([ctx["country"] for ctx in contexts]), key=[ctx["country"] for ctx in contexts].count) if contexts else "none",
            "cultural_diversity_score": len(countries_visited),
            "etiquette_experience_level": self._calculate_experience_level(len(contexts))
        }
    
    def _calculate_experience_level(self, interaction_count: int) -> str:
        """Calculate user's cultural etiquette experience level"""
        if interaction_count == 0:
            return "Beginner"
        elif interaction_count < 5:
            return "Novice"
        elif interaction_count < 15:
            return "Intermediate"
        elif interaction_count < 30:
            return "Advanced"
        else:
            return "Expert"

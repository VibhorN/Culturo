"""
Pronunciation Coach Agent
Provides real-time pronunciation analysis and personalized coaching
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


class PronunciationCoachAgent(BaseAgent):
    """
    Provides pronunciation coaching through:
    - Real-time pronunciation analysis
    - Phonetic breakdowns and mouth positioning tips
    - Personalized pronunciation exercises
    - Progress tracking over time
    """
    
    def __init__(self, anthropic_api_key: str, deepgram_api_key: str = None):
        super().__init__("PronunciationCoach", anthropic_api_key)
        self.deepgram_api_key = deepgram_api_key
        self.user_progress = {}  # Store user pronunciation progress
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Analyzes pronunciation and provides coaching feedback
        """
        try:
            user_id = input_data.get("user_id", "anonymous")
            text = input_data.get("text", "")
            target_language = input_data.get("target_language", "en")
            audio_data = input_data.get("audio_data", None)
            audio_confidence = input_data.get("audio_confidence", 1.0)
            
            logger.info(f"[PronunciationCoach] Analyzing pronunciation for user {user_id}")
            
            # Get user's pronunciation history
            user_history = self.user_progress.get(user_id, {
                "common_errors": [],
                "improvement_areas": [],
                "strengths": [],
                "practice_sessions": 0,
                "accuracy_trend": []
            })
            
            # Analyze pronunciation
            analysis = await self._analyze_pronunciation(
                text, target_language, audio_data, audio_confidence, user_history
            )
            
            # Update user progress
            self._update_user_progress(user_id, analysis)
            
            # Generate personalized exercises
            exercises = await self._generate_exercises(user_id, analysis)
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data={
                    "pronunciation_analysis": analysis,
                    "personalized_exercises": exercises,
                    "progress_summary": self._get_progress_summary(user_id),
                    "next_practice_focus": analysis.get("priority_focus", "")
                },
                confidence=analysis.get("confidence", 0.8),
                reasoning=analysis.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"[PronunciationCoach] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _analyze_pronunciation(self, text: str, target_lang: str, audio_data: any, 
                                   audio_conf: float, user_history: Dict) -> Dict:
        """Analyze pronunciation using AI and provide detailed feedback"""
        try:
            prompt = f"""
            You are a pronunciation coach expert. Analyze this text for pronunciation challenges.
            
            Text: "{text}"
            Target Language: {target_lang}
            Audio Confidence: {audio_conf} (lower means possibly misheard)
            User History: {json.dumps(user_history)}
            
            Provide detailed analysis:
            1. Phonetic breakdown of challenging sounds
            2. Common pronunciation errors for this text
            3. Mouth positioning and articulation tips
            4. Rhythm and stress patterns
            5. Comparison with user's historical errors
            6. Specific areas needing improvement
            7. Confidence in analysis (0-1)
            
            Focus on sounds that are typically difficult for speakers of common native languages.
            
            Respond in JSON:
            {{
                "phonetic_breakdown": [
                    {{"word": "...", "phonetic": "...", "difficulty": "easy/medium/hard"}}
                ],
                "common_errors": [
                    {{"sound": "...", "error": "...", "correction": "...", "tip": "..."}}
                ],
                "articulation_tips": [
                    {{"sound": "...", "mouth_position": "...", "breathing": "...", "practice_method": "..."}}
                ],
                "rhythm_patterns": {{
                    "stress_pattern": "...",
                    "syllable_count": 0,
                    "rhythm_tips": ["tip1", "tip2"]
                }},
                "difficulty_assessment": "beginner/intermediate/advanced",
                "priority_focus": "most important area to practice",
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
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1200,
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
                    
                    # Log API call
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
                        analysis_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(analysis_text[start_idx:end_idx])
                    
        except Exception as e:
            logger.error(f"[PronunciationCoach] Error analyzing pronunciation: {str(e)}")
        
        return {
            "phonetic_breakdown": [],
            "common_errors": [],
            "articulation_tips": [],
            "rhythm_patterns": {"stress_pattern": "", "syllable_count": 0, "rhythm_tips": []},
            "difficulty_assessment": "unknown",
            "priority_focus": "general pronunciation",
            "confidence": 0.3,
            "reasoning": "Unable to analyze pronunciation"
        }
    
    async def _generate_exercises(self, user_id: str, analysis: Dict) -> List[Dict]:
        """Generate personalized pronunciation exercises based on analysis"""
        try:
            user_history = self.user_progress.get(user_id, {})
            common_errors = analysis.get("common_errors", [])
            priority_focus = analysis.get("priority_focus", "")
            
            prompt = f"""
            Generate personalized pronunciation exercises for this user.
            
            Analysis: {json.dumps(analysis)}
            User History: {json.dumps(user_history)}
            Priority Focus: {priority_focus}
            
            Create 3-5 targeted exercises that address:
            1. The most critical pronunciation issues
            2. Progressive difficulty levels
            3. Engaging and varied practice methods
            4. Specific sounds and patterns to practice
            
            Respond in JSON:
            {{
                "exercises": [
                    {{
                        "id": "exercise_1",
                        "type": "minimal_pairs/tongue_twister/rhythm_practice/word_focus",
                        "title": "...",
                        "description": "...",
                        "target_sounds": ["sound1", "sound2"],
                        "difficulty": "beginner/intermediate/advanced",
                        "instructions": ["step1", "step2", "step3"],
                        "practice_text": "...",
                        "expected_duration": "2-3 minutes",
                        "success_criteria": "..."
                    }}
                ],
                "practice_schedule": {{
                    "daily_focus": "...",
                    "weekly_goals": ["goal1", "goal2"],
                    "recommended_frequency": "daily/3x_week"
                }}
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
                        exercises_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = exercises_text.find('{')
            end_idx = exercises_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(exercises_text[start_idx:end_idx]).get("exercises", [])
                    
        except Exception as e:
            logger.error(f"[PronunciationCoach] Error generating exercises: {str(e)}")
        
        return []
    
    def _update_user_progress(self, user_id: str, analysis: Dict):
        """Update user's pronunciation progress tracking"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                "common_errors": [],
                "improvement_areas": [],
                "strengths": [],
                "practice_sessions": 0,
                "accuracy_trend": []
            }
        
        # Update practice sessions
        self.user_progress[user_id]["practice_sessions"] += 1
        
        # Track common errors
        for error in analysis.get("common_errors", []):
            sound = error.get("sound", "")
            if sound not in [e.get("sound", "") for e in self.user_progress[user_id]["common_errors"]]:
                self.user_progress[user_id]["common_errors"].append({
                    "sound": sound,
                    "frequency": 1,
                    "last_practiced": time.time()
                })
            else:
                # Update frequency
                for e in self.user_progress[user_id]["common_errors"]:
                    if e.get("sound") == sound:
                        e["frequency"] += 1
                        e["last_practiced"] = time.time()
                        break
        
        # Track improvement areas
        priority_focus = analysis.get("priority_focus", "")
        if priority_focus and priority_focus not in self.user_progress[user_id]["improvement_areas"]:
            self.user_progress[user_id]["improvement_areas"].append(priority_focus)
    
    def _get_progress_summary(self, user_id: str) -> Dict:
        """Get a summary of user's pronunciation progress"""
        if user_id not in self.user_progress:
            return {"status": "new_user", "message": "Welcome! Let's start your pronunciation journey."}
        
        history = self.user_progress[user_id]
        sessions = history["practice_sessions"]
        common_errors = len(history["common_errors"])
        improvement_areas = len(history["improvement_areas"])
        
        if sessions < 5:
            level = "beginner"
        elif sessions < 20:
            level = "intermediate"
        else:
            level = "advanced"
        
        return {
            "level": level,
            "practice_sessions": sessions,
            "common_errors_tracked": common_errors,
            "improvement_areas": improvement_areas,
            "most_frequent_error": max(history["common_errors"], key=lambda x: x.get("frequency", 0)).get("sound", "none") if history["common_errors"] else "none",
            "encouragement": self._get_encouragement_message(sessions, level)
        }
    
    def _get_encouragement_message(self, sessions: int, level: str) -> str:
        """Generate encouraging messages based on progress"""
        if sessions == 1:
            return "Great start! Every expert was once a beginner."
        elif sessions < 5:
            return "You're building great habits! Consistency is key to improvement."
        elif sessions < 10:
            return "Excellent progress! You're developing a strong foundation."
        elif sessions < 20:
            return "Outstanding dedication! Your pronunciation is noticeably improving."
        else:
            return "You're a pronunciation champion! Keep inspiring others with your progress."

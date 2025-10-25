"""
Motivation Coach Agent
Tracks learning streaks, celebrates achievements, and provides personalized motivation
"""

import json
import logging
import aiohttp
import time
import random
from typing import Dict, List
from datetime import datetime, timedelta
from ..base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

# Import logging system
try:
    from utils.logging import log_api_call
    from utils.persistence import persistence
except ImportError:
    def log_api_call(*args, **kwargs):
        pass
    # Mock persistence for testing
    class MockPersistence:
        def save_user_data(self, agent_name, user_id, data): pass
        def load_user_data(self, agent_name, user_id): return {}
    persistence = MockPersistence()


class MotivationCoachAgent(BaseAgent):
    """
    Provides motivation and engagement through:
    - Learning streak tracking and celebration
    - Achievement recognition and rewards
    - Personalized encouragement and challenges
    - Progress milestone celebrations
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("MotivationCoach", anthropic_api_key)
        self.user_motivation = {}  # Store user motivation data
        self.achievement_system = {}  # Track achievements
        self.persistence = persistence
        self.motivation_templates = {
            "encouragement": [
                "You're doing amazing! Every step forward is progress.",
                "Your dedication is inspiring! Keep up the great work.",
                "Learning a new language is a journey, and you're on the right path!",
                "Consistency is your superpower! You're building something incredible.",
                "Every word you learn brings you closer to your goals!"
            ],
            "celebration": [
                "🎉 Congratulations! You've reached a new milestone!",
                "🌟 Outstanding work! Your progress is remarkable!",
                "🏆 You're a language learning champion!",
                "✨ Amazing achievement! You should be proud!",
                "🎯 Perfect! You're hitting your targets consistently!"
            ],
            "challenge": [
                "Ready for a new challenge? Let's push your limits!",
                "Time to level up! Here's your next mission.",
                "You've mastered the basics - now let's tackle something exciting!",
                "Challenge accepted? Let's see what you're made of!",
                "Ready to unlock your next achievement?"
            ]
        }
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Provides motivation and tracks achievements
        """
        try:
            user_id = input_data.get("user_id", "anonymous")
            action = input_data.get("action", "check_motivation")  # check_motivation, celebrate_achievement, get_challenge, update_progress
            progress_data = input_data.get("progress_data", {})
            
            logger.info(f"[MotivationCoach] Processing {action} for user {user_id}")
            
            # Initialize user motivation data if needed
            if user_id not in self.user_motivation:
                # Try to load from persistence first
                saved_data = self.persistence.load_user_data("MotivationCoach", user_id)
                if saved_data:
                    self.user_motivation[user_id] = saved_data
                else:
                    self.user_motivation[user_id] = {
                        "current_streak": 0,
                        "longest_streak": 0,
                        "total_sessions": 0,
                        "achievements": [],
                        "milestones": [],
                        "motivation_level": "high",
                        "last_session_date": None,
                        "personal_records": {},
                        "challenges_completed": 0,
                        "encouragement_history": []
                    }
            
            if action == "check_motivation":
                result = await self._check_motivation_status(user_id, progress_data)
            elif action == "celebrate_achievement":
                achievement_type = input_data.get("achievement_type", "session_completed")
                result = await self._celebrate_achievement(user_id, achievement_type, progress_data)
            elif action == "get_challenge":
                difficulty = input_data.get("difficulty", "intermediate")
                result = await self._generate_challenge(user_id, difficulty)
            elif action == "update_progress":
                result = await self._update_progress(user_id, progress_data)
            else:
                result = {"error": "Unknown action"}
            
            # Save updated data to persistence
            self.persistence.save_user_data("MotivationCoach", user_id, self.user_motivation[user_id])
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data=result,
                confidence=0.9,
                reasoning=f"Processed {action} request successfully"
            )
            
        except Exception as e:
            logger.error(f"[MotivationCoach] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _check_motivation_status(self, user_id: str, progress_data: Dict) -> Dict:
        """Check user's motivation status and provide encouragement"""
        try:
            user_data = self.user_motivation[user_id]
            current_time = datetime.now()
            
            # Update streak based on recent activity
            self._update_streak(user_id, progress_data)
            
            # Check for milestones
            milestones = self._check_milestones(user_id, progress_data)
            
            # Generate personalized encouragement
            encouragement = await self._generate_encouragement(user_id, progress_data)
            
            # Assess motivation level
            motivation_assessment = await self._assess_motivation_level(user_id, progress_data)
            
            return {
                "motivation_status": {
                    "current_streak": user_data["current_streak"],
                    "longest_streak": user_data["longest_streak"],
                    "total_sessions": user_data["total_sessions"],
                    "motivation_level": user_data["motivation_level"],
                    "last_session": user_data["last_session_date"]
                },
                "milestones": milestones,
                "encouragement": encouragement,
                "motivation_assessment": motivation_assessment,
                "next_achievement": self._get_next_achievement(user_id),
                "streak_status": self._get_streak_status(user_data["current_streak"])
            }
                    
        except Exception as e:
            logger.error(f"[MotivationCoach] Error checking motivation: {str(e)}")
        
        return {
            "motivation_status": {"current_streak": 0, "longest_streak": 0, "total_sessions": 0, "motivation_level": "unknown", "last_session": None},
            "milestones": [],
            "encouragement": {"message": "Keep up the great work!", "type": "general"},
            "motivation_assessment": {"level": "unknown", "trend": "stable"},
            "next_achievement": {"name": "First Session", "progress": 0, "target": 1},
            "streak_status": "new_user"
        }
    
    async def _celebrate_achievement(self, user_id: str, achievement_type: str, progress_data: Dict) -> Dict:
        """Celebrate user achievements and provide rewards"""
        try:
            user_data = self.user_motivation[user_id]
            
            # Generate celebration message
            celebration = await self._generate_celebration(user_id, achievement_type, progress_data)
            
            # Award achievement if new
            achievement = self._award_achievement(user_id, achievement_type, progress_data)
            
            # Update personal records
            self._update_personal_records(user_id, achievement_type, progress_data)
            
            # Generate next challenge
            next_challenge = await self._generate_challenge(user_id, "adaptive")
            
            return {
                "celebration": celebration,
                "achievement": achievement,
                "personal_records": user_data["personal_records"],
                "next_challenge": next_challenge,
                "motivation_boost": self._calculate_motivation_boost(achievement_type),
                "social_sharing": self._generate_social_message(user_id, achievement_type)
            }
                    
        except Exception as e:
            logger.error(f"[MotivationCoach] Error celebrating achievement: {str(e)}")
        
        return {
            "celebration": {"message": "Great job!", "type": "general"},
            "achievement": {"name": "Unknown", "new": False, "description": ""},
            "personal_records": {},
            "next_challenge": {"name": "Keep Learning", "description": "Continue your journey"},
            "motivation_boost": 0.1,
            "social_sharing": "I'm making great progress in my language learning journey!"
        }
    
    async def _generate_challenge(self, user_id: str, difficulty: str) -> Dict:
        """Generate personalized challenges for the user"""
        try:
            user_data = self.user_motivation[user_id]
            user_level = self._determine_user_level(user_data)
            
            prompt = f"""
            Generate a personalized learning challenge for this user.
            
            User Level: {user_level}
            Difficulty: {difficulty}
            Current Streak: {user_data["current_streak"]}
            Total Sessions: {user_data["total_sessions"]}
            Completed Challenges: {user_data["challenges_completed"]}
            
            Create a challenge that is:
            1. Appropriate for their level
            2. Engaging and motivating
            3. Achievable but challenging
            4. Specific and measurable
            5. Time-bound
            
            Respond in JSON:
            {{
                "challenge_name": "...",
                "description": "...",
                "objectives": ["objective1", "objective2", "objective3"],
                "success_criteria": "...",
                "time_limit": "X days",
                "difficulty": "beginner/intermediate/advanced",
                "reward": "...",
                "motivation_message": "...",
                "tips": ["tip1", "tip2"],
                "progress_tracking": "..."
            }}
            """
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 800,
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
                        challenge_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = challenge_text.find('{')
            end_idx = challenge_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(challenge_text[start_idx:end_idx])
                    
        except Exception as e:
            logger.error(f"[MotivationCoach] Error generating challenge: {str(e)}")
        
        return {
            "challenge_name": "Daily Practice Challenge",
            "description": "Complete your daily language learning practice",
            "objectives": ["Practice for 15 minutes", "Learn 5 new words", "Complete one exercise"],
            "success_criteria": "Complete all objectives",
            "time_limit": "1 day",
            "difficulty": "beginner",
            "reward": "Achievement badge",
            "motivation_message": "You've got this!",
            "tips": ["Set a reminder", "Find a quiet space"],
            "progress_tracking": "Track daily completion"
        }
    
    async def _update_progress(self, user_id: str, progress_data: Dict) -> Dict:
        """Update user progress and provide feedback"""
        try:
            user_data = self.user_motivation[user_id]
            
            # Update session count
            if progress_data.get("session_completed", False):
                user_data["total_sessions"] += 1
                user_data["last_session_date"] = datetime.now().isoformat()
            
            # Update streak
            self._update_streak(user_id, progress_data)
            
            # Check for new achievements
            new_achievements = self._check_new_achievements(user_id, progress_data)
            
            # Generate progress feedback
            feedback = await self._generate_progress_feedback(user_id, progress_data)
            
            return {
                "updated_stats": {
                    "total_sessions": user_data["total_sessions"],
                    "current_streak": user_data["current_streak"],
                    "longest_streak": user_data["longest_streak"]
                },
                "new_achievements": new_achievements,
                "progress_feedback": feedback,
                "motivation_level": user_data["motivation_level"]
            }
                    
        except Exception as e:
            logger.error(f"[MotivationCoach] Error updating progress: {str(e)}")
        
        return {
            "updated_stats": {"total_sessions": 0, "current_streak": 0, "longest_streak": 0},
            "new_achievements": [],
            "progress_feedback": {"message": "Keep going!", "type": "general"},
            "motivation_level": "unknown"
        }
    
    async def _generate_encouragement(self, user_id: str, progress_data: Dict) -> Dict:
        """Generate personalized encouragement messages"""
        try:
            user_data = self.user_motivation[user_id]
            streak = user_data["current_streak"]
            total_sessions = user_data["total_sessions"]
            
            # Determine encouragement type based on context
            if streak >= 7:
                encouragement_type = "streak_celebration"
            elif total_sessions < 5:
                encouragement_type = "beginner"
            elif progress_data.get("struggling", False):
                encouragement_type = "support"
            else:
                encouragement_type = "general"
            
            # Generate contextual encouragement
            if encouragement_type == "streak_celebration":
                message = f"🔥 Amazing {streak}-day streak! You're building incredible momentum!"
            elif encouragement_type == "beginner":
                message = "🌟 Welcome to your language learning journey! Every expert was once a beginner."
            elif encouragement_type == "support":
                message = "💪 Learning can be challenging, but you're stronger than any obstacle!"
            else:
                message = random.choice(self.motivation_templates["encouragement"])
            
            return {
                "message": message,
                "type": encouragement_type,
                "motivation_boost": 0.2,
                "personalized": True
            }
                    
        except Exception as e:
            logger.error(f"[MotivationCoach] Error generating encouragement: {str(e)}")
        
        return {
            "message": "Keep up the great work!",
            "type": "general",
            "motivation_boost": 0.1,
            "personalized": False
        }
    
    async def _generate_celebration(self, user_id: str, achievement_type: str, progress_data: Dict) -> Dict:
        """Generate celebration messages for achievements"""
        try:
            user_data = self.user_motivation[user_id]
            
            # Generate contextual celebration
            if achievement_type == "streak_milestone":
                streak = user_data["current_streak"]
                message = f"🎉 {streak} days strong! You're unstoppable!"
            elif achievement_type == "vocabulary_milestone":
                words_learned = progress_data.get("words_learned", 0)
                message = f"📚 {words_learned} words mastered! Your vocabulary is growing!"
            elif achievement_type == "session_completed":
                message = "✅ Session complete! Every step counts!"
            else:
                message = random.choice(self.motivation_templates["celebration"])
            
            return {
                "message": message,
                "type": achievement_type,
                "celebration_level": "high" if achievement_type in ["streak_milestone", "vocabulary_milestone"] else "medium",
                "social_shareable": True
            }
                    
        except Exception as e:
            logger.error(f"[MotivationCoach] Error generating celebration: {str(e)}")
        
        return {
            "message": "Great job!",
            "type": "general",
            "celebration_level": "medium",
            "social_shareable": True
        }
    
    async def _assess_motivation_level(self, user_id: str, progress_data: Dict) -> Dict:
        """Assess user's current motivation level"""
        try:
            user_data = self.user_motivation[user_id]
            
            # Calculate motivation score based on various factors
            streak_score = min(user_data["current_streak"] / 30, 1.0)  # Max at 30 days
            consistency_score = min(user_data["total_sessions"] / 100, 1.0)  # Max at 100 sessions
            recent_activity = 1.0 if user_data["last_session_date"] else 0.0
            
            motivation_score = (streak_score * 0.4 + consistency_score * 0.4 + recent_activity * 0.2)
            
            if motivation_score >= 0.8:
                level = "high"
                trend = "increasing"
            elif motivation_score >= 0.5:
                level = "medium"
                trend = "stable"
            else:
                level = "low"
                trend = "declining"
            
            return {
                "level": level,
                "score": motivation_score,
                "trend": trend,
                "factors": {
                    "streak_contribution": streak_score,
                    "consistency_contribution": consistency_score,
                    "recent_activity": recent_activity
                }
            }
                    
        except Exception as e:
            logger.error(f"[MotivationCoach] Error assessing motivation: {str(e)}")
        
        return {
            "level": "unknown",
            "score": 0.0,
            "trend": "stable",
            "factors": {"streak_contribution": 0.0, "consistency_contribution": 0.0, "recent_activity": 0.0}
        }
    
    def _update_streak(self, user_id: str, progress_data: Dict):
        """Update user's learning streak"""
        user_data = self.user_motivation[user_id]
        current_time = datetime.now()
        
        if progress_data.get("session_completed", False):
            if user_data["last_session_date"]:
                last_session = datetime.fromisoformat(user_data["last_session_date"])
                days_diff = (current_time - last_session).days
                
                if days_diff == 1:
                    user_data["current_streak"] += 1
                elif days_diff > 1:
                    user_data["current_streak"] = 1  # Reset streak
                # If days_diff == 0, same day, don't increment
            else:
                user_data["current_streak"] = 1
            
            user_data["last_session_date"] = current_time.isoformat()
            user_data["longest_streak"] = max(user_data["longest_streak"], user_data["current_streak"])
    
    def _check_milestones(self, user_id: str, progress_data: Dict) -> List[Dict]:
        """Check for milestone achievements"""
        milestones = []
        user_data = self.user_motivation[user_id]
        
        # Streak milestones
        streak = user_data["current_streak"]
        if streak in [3, 7, 14, 30, 60, 100]:
            milestones.append({
                "type": "streak",
                "value": streak,
                "message": f"🎯 {streak}-day streak achieved!",
                "new": streak not in [m["value"] for m in user_data["milestones"] if m["type"] == "streak"]
            })
        
        # Session milestones
        sessions = user_data["total_sessions"]
        if sessions in [10, 25, 50, 100, 250, 500]:
            milestones.append({
                "type": "sessions",
                "value": sessions,
                "message": f"📚 {sessions} sessions completed!",
                "new": sessions not in [m["value"] for m in user_data["milestones"] if m["type"] == "sessions"]
            })
        
        return milestones
    
    def _award_achievement(self, user_id: str, achievement_type: str, progress_data: Dict) -> Dict:
        """Award achievements to users"""
        user_data = self.user_motivation[user_id]
        
        achievement_map = {
            "first_session": {"name": "Getting Started", "description": "Completed your first learning session"},
            "streak_3": {"name": "Consistent Learner", "description": "Maintained a 3-day learning streak"},
            "streak_7": {"name": "Week Warrior", "description": "Maintained a 7-day learning streak"},
            "streak_30": {"name": "Monthly Master", "description": "Maintained a 30-day learning streak"},
            "vocabulary_100": {"name": "Word Wizard", "description": "Learned 100 vocabulary words"},
            "vocabulary_500": {"name": "Vocabulary Virtuoso", "description": "Learned 500 vocabulary words"}
        }
        
        achievement = achievement_map.get(achievement_type, {"name": "Unknown Achievement", "description": ""})
        
        # Check if already awarded
        if achievement["name"] not in user_data["achievements"]:
            user_data["achievements"].append(achievement["name"])
            return {**achievement, "new": True}
        else:
            return {**achievement, "new": False}
    
    def _update_personal_records(self, user_id: str, achievement_type: str, progress_data: Dict):
        """Update user's personal records"""
        user_data = self.user_motivation[user_id]
        
        if achievement_type == "longest_streak":
            current_streak = user_data["current_streak"]
            if current_streak > user_data["personal_records"].get("longest_streak", 0):
                user_data["personal_records"]["longest_streak"] = current_streak
        
        elif achievement_type == "most_words_session":
            words_learned = progress_data.get("words_learned", 0)
            if words_learned > user_data["personal_records"].get("most_words_session", 0):
                user_data["personal_records"]["most_words_session"] = words_learned
    
    def _calculate_motivation_boost(self, achievement_type: str) -> float:
        """Calculate motivation boost based on achievement type"""
        boost_map = {
            "first_session": 0.3,
            "streak_3": 0.2,
            "streak_7": 0.3,
            "streak_30": 0.5,
            "vocabulary_100": 0.4,
            "vocabulary_500": 0.6
        }
        return boost_map.get(achievement_type, 0.1)
    
    def _generate_social_message(self, user_id: str, achievement_type: str) -> str:
        """Generate social media sharing messages"""
        user_data = self.user_motivation[user_id]
        
        if achievement_type == "streak_milestone":
            streak = user_data["current_streak"]
            return f"🔥 {streak} days of language learning! Consistency is key! #LanguageLearning #Streak"
        elif achievement_type == "vocabulary_milestone":
            return "📚 Expanding my vocabulary one word at a time! #Vocabulary #LanguageLearning"
        else:
            return "🌟 Making progress in my language learning journey! #LanguageLearning #Progress"
    
    def _get_next_achievement(self, user_id: str) -> Dict:
        """Get the next achievable milestone"""
        user_data = self.user_motivation[user_id]
        
        # Find next streak milestone
        current_streak = user_data["current_streak"]
        streak_milestones = [3, 7, 14, 30, 60, 100]
        next_streak = next((m for m in streak_milestones if m > current_streak), None)
        
        if next_streak:
            return {
                "name": f"{next_streak}-Day Streak",
                "progress": current_streak,
                "target": next_streak,
                "type": "streak"
            }
        
        # Find next session milestone
        current_sessions = user_data["total_sessions"]
        session_milestones = [10, 25, 50, 100, 250, 500]
        next_sessions = next((m for m in session_milestones if m > current_sessions), None)
        
        if next_sessions:
            return {
                "name": f"{next_sessions} Sessions",
                "progress": current_sessions,
                "target": next_sessions,
                "type": "sessions"
            }
        
        return {"name": "Keep Learning", "progress": 0, "target": 1, "type": "general"}
    
    def _get_streak_status(self, current_streak: int) -> str:
        """Get streak status message"""
        if current_streak == 0:
            return "new_user"
        elif current_streak < 3:
            return "building_momentum"
        elif current_streak < 7:
            return "getting_consistent"
        elif current_streak < 30:
            return "strong_streak"
        else:
            return "streak_master"
    
    def _determine_user_level(self, user_data: Dict) -> str:
        """Determine user's learning level"""
        total_sessions = user_data["total_sessions"]
        
        if total_sessions < 10:
            return "beginner"
        elif total_sessions < 50:
            return "intermediate"
        else:
            return "advanced"
    
    def _check_new_achievements(self, user_id: str, progress_data: Dict) -> List[Dict]:
        """Check for new achievements based on progress"""
        new_achievements = []
        user_data = self.user_motivation[user_id]
        
        # Check streak achievements
        if user_data["current_streak"] == 3 and "Consistent Learner" not in user_data["achievements"]:
            new_achievements.append({"name": "Consistent Learner", "description": "3-day streak!"})
        
        if user_data["current_streak"] == 7 and "Week Warrior" not in user_data["achievements"]:
            new_achievements.append({"name": "Week Warrior", "description": "7-day streak!"})
        
        # Check session achievements
        if user_data["total_sessions"] == 10 and "Getting Started" not in user_data["achievements"]:
            new_achievements.append({"name": "Getting Started", "description": "10 sessions completed!"})
        
        return new_achievements
    
    async def _generate_progress_feedback(self, user_id: str, progress_data: Dict) -> Dict:
        """Generate progress feedback"""
        user_data = self.user_motivation[user_id]
        
        if user_data["current_streak"] > user_data.get("previous_streak", 0):
            return {"message": "Your streak is growing! Keep it up!", "type": "positive"}
        elif user_data["total_sessions"] > user_data.get("previous_sessions", 0):
            return {"message": "Great progress! Every session counts!", "type": "encouraging"}
        else:
            return {"message": "Ready for your next session?", "type": "motivational"}

"""
Vocabulary Builder Agent
Implements spaced repetition and context-aware vocabulary learning
"""

import json
import logging
import aiohttp
import time
import math
from typing import Dict, List, Set
from datetime import datetime, timedelta
from ..base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

# Import logging system
try:
    from utils.logging import log_api_call
except ImportError:
    def log_api_call(*args, **kwargs):
        pass


class VocabularyBuilderAgent(BaseAgent):
    """
    Advanced vocabulary learning through:
    - Spaced repetition algorithm for optimal retention
    - Context-aware word suggestions
    - Personalized flashcards and word lists
    - Progress tracking and review scheduling
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("VocabularyBuilder", anthropic_api_key)
        self.user_vocabularies = {}  # Store user vocabulary data
        self.spaced_repetition_intervals = [1, 3, 7, 14, 30, 90, 180, 365]  # Days
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Processes vocabulary learning requests
        """
        try:
            user_id = input_data.get("user_id", "anonymous")
            action = input_data.get("action", "suggest_words")  # suggest_words, review_words, add_words, get_progress
            context = input_data.get("context", {})
            target_language = input_data.get("target_language", "en")
            
            logger.info(f"[VocabularyBuilder] Processing {action} for user {user_id}")
            
            # Initialize user vocabulary if needed
            if user_id not in self.user_vocabularies:
                self.user_vocabularies[user_id] = {
                    "known_words": {},
                    "learning_words": {},
                    "mastered_words": {},
                    "learning_preferences": {
                        "difficulty_preference": "intermediate",
                        "topics_of_interest": [],
                        "daily_word_goal": 10
                    },
                    "statistics": {
                        "total_words_learned": 0,
                        "current_streak": 0,
                        "longest_streak": 0,
                        "last_study_date": None
                    }
                }
            
            if action == "suggest_words":
                result = await self._suggest_words(user_id, context, target_language)
            elif action == "review_words":
                result = await self._get_review_words(user_id)
            elif action == "add_words":
                words = input_data.get("words", [])
                result = await self._add_words(user_id, words, target_language)
            elif action == "get_progress":
                result = await self._get_progress_summary(user_id)
            else:
                result = {"error": "Unknown action"}
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data=result,
                confidence=0.9,
                reasoning=f"Processed {action} request successfully"
            )
            
        except Exception as e:
            logger.error(f"[VocabularyBuilder] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _suggest_words(self, user_id: str, context: Dict, target_language: str) -> Dict:
        """Suggest new words based on context and user's learning level"""
        try:
            user_vocab = self.user_vocabularies[user_id]
            conversation_topic = context.get("topic", "")
            user_level = user_vocab["learning_preferences"]["difficulty_preference"]
            
            prompt = f"""
            You are a vocabulary learning expert. Suggest 5-8 new words for this user to learn.
            
            Target Language: {target_language}
            User Level: {user_level}
            Conversation Topic: "{conversation_topic}"
            User's Known Words: {list(user_vocab["known_words"].keys())[:20]}  # Show first 20 for context
            
            Select words that are:
            1. Relevant to the conversation topic
            2. Appropriate for the user's level
            3. Commonly used in daily conversation
            4. Not already known by the user
            5. Include a mix of nouns, verbs, adjectives
            
            For each word, provide:
            - Word and part of speech
            - Definition and example sentence
            - Difficulty level
            - Learning tips or memory aids
            - Cultural context if relevant
            
            Respond in JSON:
            {{
                "suggested_words": [
                    {{
                        "word": "...",
                        "part_of_speech": "noun/verb/adjective/adverb",
                        "definition": "...",
                        "example_sentence": "...",
                        "difficulty": "beginner/intermediate/advanced",
                        "learning_tip": "...",
                        "cultural_context": "...",
                        "pronunciation": "...",
                        "related_words": ["word1", "word2"]
                    }}
                ],
                "learning_strategy": "explanation of why these words were chosen",
                "estimated_time": "5-10 minutes"
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
                start_time = time.time()
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
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
                        suggestions_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = suggestions_text.find('{')
            end_idx = suggestions_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(suggestions_text[start_idx:end_idx])
                    
        except Exception as e:
            logger.error(f"[VocabularyBuilder] Error suggesting words: {str(e)}")
        
        return {
            "suggested_words": [],
            "learning_strategy": "Unable to generate suggestions",
            "estimated_time": "unknown"
        }
    
    async def _get_review_words(self, user_id: str) -> Dict:
        """Get words that are due for review based on spaced repetition"""
        try:
            user_vocab = self.user_vocabularies[user_id]
            current_time = datetime.now()
            words_due_for_review = []
            
            # Check learning words for review
            for word, data in user_vocab["learning_words"].items():
                last_reviewed = datetime.fromisoformat(data.get("last_reviewed", current_time.isoformat()))
                interval_days = self.spaced_repetition_intervals[min(data.get("repetition_count", 0), len(self.spaced_repetition_intervals) - 1)]
                next_review = last_reviewed + timedelta(days=interval_days)
                
                if current_time >= next_review:
                    words_due_for_review.append({
                        "word": word,
                        "data": data,
                        "days_overdue": (current_time - next_review).days
                    })
            
            # Sort by days overdue (most overdue first)
            words_due_for_review.sort(key=lambda x: x["days_overdue"], reverse=True)
            
            # Limit to reasonable number for one session
            review_words = words_due_for_review[:10]
            
            return {
                "review_words": [
                    {
                        "word": item["word"],
                        "definition": item["data"].get("definition", ""),
                        "example": item["data"].get("example", ""),
                        "last_reviewed": item["data"].get("last_reviewed", ""),
                        "repetition_count": item["data"].get("repetition_count", 0),
                        "difficulty": item["data"].get("difficulty", "unknown")
                    }
                    for item in review_words
                ],
                "total_due": len(words_due_for_review),
                "session_count": len(review_words),
                "encouragement": self._get_review_encouragement(len(review_words))
            }
                    
        except Exception as e:
            logger.error(f"[VocabularyBuilder] Error getting review words: {str(e)}")
        
        return {
            "review_words": [],
            "total_due": 0,
            "session_count": 0,
            "encouragement": "No words due for review right now!"
        }
    
    async def _add_words(self, user_id: str, words: List[Dict], target_language: str) -> Dict:
        """Add new words to user's learning vocabulary"""
        try:
            user_vocab = self.user_vocabularies[user_id]
            added_words = []
            
            for word_data in words:
                word = word_data.get("word", "").lower().strip()
                if word and word not in user_vocab["known_words"] and word not in user_vocab["learning_words"]:
                    # Add to learning words
                    user_vocab["learning_words"][word] = {
                        "definition": word_data.get("definition", ""),
                        "example": word_data.get("example_sentence", ""),
                        "difficulty": word_data.get("difficulty", "intermediate"),
                        "added_date": datetime.now().isoformat(),
                        "last_reviewed": datetime.now().isoformat(),
                        "repetition_count": 0,
                        "success_count": 0,
                        "learning_tip": word_data.get("learning_tip", ""),
                        "cultural_context": word_data.get("cultural_context", "")
                    }
                    added_words.append(word)
            
            # Update statistics
            user_vocab["statistics"]["total_words_learned"] += len(added_words)
            
            return {
                "added_words": added_words,
                "count": len(added_words),
                "message": f"Successfully added {len(added_words)} new words to your vocabulary!"
            }
                    
        except Exception as e:
            logger.error(f"[VocabularyBuilder] Error adding words: {str(e)}")
        
        return {
            "added_words": [],
            "count": 0,
            "message": "Unable to add words"
        }
    
    def _get_progress_summary(self, user_id: str) -> Dict:
        """Get comprehensive progress summary for user"""
        if user_id not in self.user_vocabularies:
            return {"status": "new_user", "message": "Start learning your first words!"}
        
        user_vocab = self.user_vocabularies[user_id]
        stats = user_vocab["statistics"]
        
        # Calculate learning metrics
        total_words = len(user_vocab["learning_words"]) + len(user_vocab["mastered_words"])
        mastered_words = len(user_vocab["mastered_words"])
        learning_words = len(user_vocab["learning_words"])
        
        # Calculate mastery percentage
        mastery_percentage = (mastered_words / total_words * 100) if total_words > 0 else 0
        
        # Determine learning level
        if total_words < 50:
            level = "Beginner"
        elif total_words < 200:
            level = "Intermediate"
        elif total_words < 500:
            level = "Advanced"
        else:
            level = "Expert"
        
        # Get words due for review
        current_time = datetime.now()
        words_due = 0
        for word, data in user_vocab["learning_words"].items():
            last_reviewed = datetime.fromisoformat(data.get("last_reviewed", current_time.isoformat()))
            interval_days = self.spaced_repetition_intervals[min(data.get("repetition_count", 0), len(self.spaced_repetition_intervals) - 1)]
            next_review = last_reviewed + timedelta(days=interval_days)
            if current_time >= next_review:
                words_due += 1
        
        return {
            "level": level,
            "total_words": total_words,
            "mastered_words": mastered_words,
            "learning_words": learning_words,
            "mastery_percentage": round(mastery_percentage, 1),
            "words_due_for_review": words_due,
            "current_streak": stats["current_streak"],
            "longest_streak": stats["longest_streak"],
            "daily_goal": user_vocab["learning_preferences"]["daily_word_goal"],
            "achievement_message": self._get_achievement_message(total_words, mastery_percentage),
            "next_milestone": self._get_next_milestone(total_words)
        }
    
    def _get_review_encouragement(self, word_count: int) -> str:
        """Generate encouraging messages for review sessions"""
        if word_count == 0:
            return "Great job! You're all caught up with your reviews!"
        elif word_count <= 3:
            return "Just a few words to review - you're doing great!"
        elif word_count <= 7:
            return "A solid review session ahead - you've got this!"
        else:
            return "Time for a comprehensive review - your vocabulary will thank you!"
    
    def _get_achievement_message(self, total_words: int, mastery_percentage: float) -> str:
        """Generate achievement messages based on progress"""
        if total_words == 0:
            return "Ready to start your vocabulary journey!"
        elif total_words < 10:
            return "Great start! Every word counts."
        elif total_words < 50:
            return "Building momentum! You're developing a strong foundation."
        elif total_words < 100:
            return "Excellent progress! Your vocabulary is growing steadily."
        elif total_words < 200:
            return "Outstanding! You're becoming quite proficient."
        elif mastery_percentage > 80:
            return "Vocabulary master! Your retention is impressive."
        else:
            return "Keep up the great work! Consistency is key to mastery."
    
    def _get_next_milestone(self, total_words: int) -> str:
        """Get the next vocabulary milestone"""
        milestones = [10, 25, 50, 100, 200, 500, 1000]
        for milestone in milestones:
            if total_words < milestone:
                return f"Next milestone: {milestone} words ({milestone - total_words} to go!)"
        return "You've reached expert level! Keep expanding your vocabulary!"
    
    def update_word_progress(self, user_id: str, word: str, success: bool):
        """Update word progress based on review success"""
        if user_id not in self.user_vocabularies:
            return
        
        user_vocab = self.user_vocabularies[user_id]
        
        if word in user_vocab["learning_words"]:
            word_data = user_vocab["learning_words"][word]
            word_data["repetition_count"] += 1
            word_data["last_reviewed"] = datetime.now().isoformat()
            
            if success:
                word_data["success_count"] += 1
                
                # Move to mastered if enough successful repetitions
                if word_data["success_count"] >= 3 and word_data["repetition_count"] >= 5:
                    user_vocab["mastered_words"][word] = word_data.copy()
                    del user_vocab["learning_words"][word]
                    logger.info(f"[VocabularyBuilder] Word '{word}' moved to mastered for user {user_id}")
    
    def update_streak(self, user_id: str):
        """Update user's study streak"""
        if user_id not in self.user_vocabularies:
            return
        
        user_vocab = self.user_vocabularies[user_id]
        stats = user_vocab["statistics"]
        current_date = datetime.now().date()
        
        if stats["last_study_date"]:
            last_date = datetime.fromisoformat(stats["last_study_date"]).date()
            if current_date == last_date:
                return  # Already studied today
            elif (current_date - last_date).days == 1:
                stats["current_streak"] += 1
            else:
                stats["current_streak"] = 1
        else:
            stats["current_streak"] = 1
        
        stats["last_study_date"] = current_date.isoformat()
        stats["longest_streak"] = max(stats["longest_streak"], stats["current_streak"])

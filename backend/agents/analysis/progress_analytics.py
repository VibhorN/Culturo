"""
Progress Analytics Agent
Deep analysis of learning patterns, trends, and personalized insights
"""

import json
import logging
import aiohttp
import time
import statistics
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from ..base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

# Import logging system
try:
    from utils.logging import log_api_call
except ImportError:
    def log_api_call(*args, **kwargs):
        pass


class ProgressAnalyticsAgent(BaseAgent):
    """
    Provides deep learning analytics through:
    - Learning pattern analysis and trend identification
    - Optimal study time and method predictions
    - Knowledge gap identification
    - Detailed progress reports and insights
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("ProgressAnalytics", anthropic_api_key)
        self.user_analytics = {}  # Store user analytics data
        self.learning_patterns = {}  # Track learning patterns across users
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Analyzes learning progress and provides insights
        """
        try:
            user_id = input_data.get("user_id", "anonymous")
            analysis_type = input_data.get("analysis_type", "comprehensive")  # comprehensive, quick, specific
            time_period = input_data.get("time_period", "30_days")  # 7_days, 30_days, 90_days, all_time
            learning_data = input_data.get("learning_data", {})
            
            logger.info(f"[ProgressAnalytics] Analyzing progress for user {user_id} - {analysis_type}")
            
            # Collect and analyze learning data
            analytics_result = await self._analyze_learning_progress(
                user_id, analysis_type, time_period, learning_data
            )
            
            # Generate insights and recommendations
            insights = await self._generate_insights(user_id, analytics_result)
            
            # Predict optimal learning strategies
            predictions = await self._predict_optimal_strategies(user_id, analytics_result)
            
            # Update user analytics
            self._update_user_analytics(user_id, analytics_result)
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data={
                    "analytics_summary": analytics_result,
                    "insights": insights,
                    "predictions": predictions,
                    "recommendations": self._generate_recommendations(analytics_result),
                    "progress_trends": self._calculate_trends(user_id),
                    "comparative_analysis": self._get_comparative_analysis(user_id)
                },
                confidence=analytics_result.get("confidence", 0.8),
                reasoning=analytics_result.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"[ProgressAnalytics] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _analyze_learning_progress(self, user_id: str, analysis_type: str, time_period: str, learning_data: Dict) -> Dict:
        """Perform comprehensive learning progress analysis"""
        try:
            # Get user's historical data
            user_data = self.user_analytics.get(user_id, {
                "study_sessions": [],
                "vocabulary_progress": [],
                "pronunciation_scores": [],
                "cultural_interactions": [],
                "learning_preferences": {},
                "achievements": [],
                "challenges": []
            })
            
            prompt = f"""
            You are a learning analytics expert. Analyze this user's learning progress comprehensively.
            
            User ID: {user_id}
            Analysis Type: {analysis_type}
            Time Period: {time_period}
            Learning Data: {json.dumps(learning_data)}
            Historical Data: {json.dumps(user_data)}
            
            Analyze:
            1. Learning velocity and acceleration
            2. Consistency patterns and streaks
            3. Skill development across different areas
            4. Engagement and motivation trends
            5. Knowledge retention rates
            6. Learning efficiency metrics
            7. Areas of strength and improvement
            8. Optimal learning times and methods
            
            Provide detailed analysis with specific metrics and trends.
            
            Respond in JSON:
            {{
                "learning_velocity": {{
                    "vocabulary_growth_rate": 0.0,
                    "pronunciation_improvement_rate": 0.0,
                    "cultural_knowledge_growth": 0.0,
                    "overall_progress_rate": 0.0
                }},
                "consistency_metrics": {{
                    "study_frequency": "daily/weekly/irregular",
                    "average_session_length": 0,
                    "longest_streak": 0,
                    "current_streak": 0,
                    "consistency_score": 0.0
                }},
                "skill_development": {{
                    "vocabulary_mastery": 0.0,
                    "pronunciation_accuracy": 0.0,
                    "cultural_awareness": 0.0,
                    "conversation_fluency": 0.0,
                    "grammar_proficiency": 0.0
                }},
                "engagement_analysis": {{
                    "session_completion_rate": 0.0,
                    "exercise_engagement": 0.0,
                    "review_participation": 0.0,
                    "motivation_level": "high/medium/low"
                }},
                "retention_metrics": {{
                    "vocabulary_retention_rate": 0.0,
                    "concept_retention_rate": 0.0,
                    "skill_decay_rate": 0.0,
                    "long_term_retention": 0.0
                }},
                "efficiency_metrics": {{
                    "time_to_mastery": 0,
                    "learning_curve_slope": 0.0,
                    "practice_efficiency": 0.0,
                    "knowledge_transfer_rate": 0.0
                }},
                "strengths": ["strength1", "strength2"],
                "improvement_areas": ["area1", "area2"],
                "learning_patterns": ["pattern1", "pattern2"],
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
                        analysis_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(analysis_text[start_idx:end_idx])
                except json.JSONDecodeError as json_err:
                    logger.error(f"[ProgressAnalytics] JSON parsing error: {str(json_err)}")
                    logger.debug(f"[ProgressAnalytics] Raw response: {analysis_text[start_idx:end_idx]}")
                    
        except Exception as e:
            logger.error(f"[ProgressAnalytics] Error analyzing progress: {str(e)}")
        
        return {
            "learning_velocity": {"vocabulary_growth_rate": 0.0, "pronunciation_improvement_rate": 0.0, "cultural_knowledge_growth": 0.0, "overall_progress_rate": 0.0},
            "consistency_metrics": {"study_frequency": "unknown", "average_session_length": 0, "longest_streak": 0, "current_streak": 0, "consistency_score": 0.0},
            "skill_development": {"vocabulary_mastery": 0.0, "pronunciation_accuracy": 0.0, "cultural_awareness": 0.0, "conversation_fluency": 0.0, "grammar_proficiency": 0.0},
            "engagement_analysis": {"session_completion_rate": 0.0, "exercise_engagement": 0.0, "review_participation": 0.0, "motivation_level": "unknown"},
            "retention_metrics": {"vocabulary_retention_rate": 0.0, "concept_retention_rate": 0.0, "skill_decay_rate": 0.0, "long_term_retention": 0.0},
            "efficiency_metrics": {"time_to_mastery": 0, "learning_curve_slope": 0.0, "practice_efficiency": 0.0, "knowledge_transfer_rate": 0.0},
            "strengths": [],
            "improvement_areas": [],
            "learning_patterns": [],
            "confidence": 0.3,
            "reasoning": "Unable to analyze progress"
        }
    
    async def _generate_insights(self, user_id: str, analytics_result: Dict) -> Dict:
        """Generate personalized insights based on analytics"""
        try:
            user_data = self.user_analytics.get(user_id, {})
            
            prompt = f"""
            Generate personalized learning insights based on analytics data.
            
            Analytics Result: {json.dumps(analytics_result)}
            User Data: {json.dumps(user_data)}
            
            Provide:
            1. Key insights about learning patterns
            2. Success factors and what's working well
            3. Potential challenges and risks
            4. Personalized recommendations
            5. Learning style identification
            6. Motivation and engagement insights
            
            Respond in JSON:
            {{
                "key_insights": [
                    {{
                        "insight": "...",
                        "significance": "high/medium/low",
                        "actionable": true/false,
                        "explanation": "..."
                    }}
                ],
                "success_factors": ["factor1", "factor2"],
                "potential_challenges": [
                    {{
                        "challenge": "...",
                        "risk_level": "high/medium/low",
                        "mitigation": "..."
                    }}
                ],
                "learning_style": {{
                    "primary_style": "visual/auditory/kinesthetic/reading",
                    "secondary_style": "...",
                    "confidence": 0.0,
                    "evidence": ["evidence1", "evidence2"]
                }},
                "motivation_insights": {{
                    "motivation_drivers": ["driver1", "driver2"],
                    "engagement_triggers": ["trigger1", "trigger2"],
                    "potential_burnout_signs": ["sign1", "sign2"],
                    "sustainability_score": 0.0
                }},
                "personalized_recommendations": [
                    {{
                        "recommendation": "...",
                        "priority": "high/medium/low",
                        "expected_impact": "...",
                        "implementation_difficulty": "easy/medium/hard"
                    }}
                ]
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
                        insights_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = insights_text.find('{')
            end_idx = insights_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(insights_text[start_idx:end_idx])
                except json.JSONDecodeError as json_err:
                    logger.error(f"[ProgressAnalytics] JSON parsing error in insights: {str(json_err)}")
                    logger.debug(f"[ProgressAnalytics] Raw insights response: {insights_text[start_idx:end_idx]}")
                    
        except Exception as e:
            logger.error(f"[ProgressAnalytics] Error generating insights: {str(e)}")
        
        return {
            "key_insights": [],
            "success_factors": [],
            "potential_challenges": [],
            "learning_style": {"primary_style": "unknown", "secondary_style": "unknown", "confidence": 0.0, "evidence": []},
            "motivation_insights": {"motivation_drivers": [], "engagement_triggers": [], "potential_burnout_signs": [], "sustainability_score": 0.0},
            "personalized_recommendations": []
        }
    
    async def _predict_optimal_strategies(self, user_id: str, analytics_result: Dict) -> Dict:
        """Predict optimal learning strategies based on patterns"""
        try:
            prompt = f"""
            Predict optimal learning strategies based on user's analytics and patterns.
            
            Analytics Result: {json.dumps(analytics_result)}
            
            Predict:
            1. Optimal study times and frequency
            2. Most effective learning methods
            3. Ideal session length and structure
            4. Best practice techniques
            5. Optimal difficulty progression
            6. Predicted learning outcomes
            
            Respond in JSON:
            {{
                "optimal_study_schedule": {{
                    "best_times": ["time1", "time2"],
                    "optimal_frequency": "daily/3x_week/weekly",
                    "session_length": 0,
                    "break_intervals": 0
                }},
                "effective_methods": [
                    {{
                        "method": "...",
                        "effectiveness_score": 0.0,
                        "reasoning": "..."
                    }}
                ],
                "session_structure": {{
                    "warm_up": "...",
                    "main_activity": "...",
                    "practice": "...",
                    "review": "...",
                    "cool_down": "..."
                }},
                "difficulty_progression": {{
                    "current_level": "...",
                    "next_milestone": "...",
                    "progression_rate": 0.0,
                    "challenge_sweet_spot": "..."
                }},
                "predicted_outcomes": {{
                    "short_term_goals": ["goal1", "goal2"],
                    "medium_term_goals": ["goal1", "goal2"],
                    "long_term_goals": ["goal1", "goal2"],
                    "timeline_estimates": {{
                        "basic_proficiency": "X weeks",
                        "intermediate_level": "X months",
                        "advanced_level": "X months"
                    }}
                }},
                "risk_factors": ["risk1", "risk2"],
                "success_probability": 0.0
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
                        predictions_text = result["content"][0]["text"]
                    else:
                        raise Exception(f"Anthropic API error: {response.status}")
            
            start_idx = predictions_text.find('{')
            end_idx = predictions_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(predictions_text[start_idx:end_idx])
                except json.JSONDecodeError as json_err:
                    logger.error(f"[ProgressAnalytics] JSON parsing error in predictions: {str(json_err)}")
                    logger.debug(f"[ProgressAnalytics] Raw predictions response: {predictions_text[start_idx:end_idx]}")
                    
        except Exception as e:
            logger.error(f"[ProgressAnalytics] Error predicting strategies: {str(e)}")
        
        return {
            "optimal_study_schedule": {"best_times": [], "optimal_frequency": "unknown", "session_length": 0, "break_intervals": 0},
            "effective_methods": [],
            "session_structure": {"warm_up": "", "main_activity": "", "practice": "", "review": "", "cool_down": ""},
            "difficulty_progression": {"current_level": "unknown", "next_milestone": "", "progression_rate": 0.0, "challenge_sweet_spot": ""},
            "predicted_outcomes": {"short_term_goals": [], "medium_term_goals": [], "long_term_goals": [], "timeline_estimates": {}},
            "risk_factors": [],
            "success_probability": 0.0
        }
    
    def _generate_recommendations(self, analytics_result: Dict) -> List[Dict]:
        """Generate actionable recommendations based on analytics"""
        recommendations = []
        
        # Analyze consistency
        consistency_score = analytics_result.get("consistency_metrics", {}).get("consistency_score", 0)
        if consistency_score < 0.6:
            recommendations.append({
                "type": "consistency",
                "priority": "high",
                "recommendation": "Improve study consistency by setting a regular schedule",
                "action": "Set daily study reminders and track streaks"
            })
        
        # Analyze engagement
        engagement = analytics_result.get("engagement_analysis", {})
        if engagement.get("session_completion_rate", 0) < 0.7:
            recommendations.append({
                "type": "engagement",
                "priority": "medium",
                "recommendation": "Increase session completion rate",
                "action": "Break sessions into smaller, manageable chunks"
            })
        
        # Analyze retention
        retention = analytics_result.get("retention_metrics", {})
        if retention.get("vocabulary_retention_rate", 0) < 0.8:
            recommendations.append({
                "type": "retention",
                "priority": "high",
                "recommendation": "Improve vocabulary retention",
                "action": "Implement spaced repetition and regular reviews"
            })
        
        return recommendations
    
    def _calculate_trends(self, user_id: str) -> Dict:
        """Calculate learning trends over time"""
        if user_id not in self.user_analytics:
            return {"status": "insufficient_data"}
        
        user_data = self.user_analytics[user_id]
        study_sessions = user_data.get("study_sessions", [])
        
        if len(study_sessions) < 7:
            return {"status": "insufficient_data", "message": "Need at least 7 days of data"}
        
        # Calculate weekly trends
        weekly_sessions = []
        for i in range(0, len(study_sessions), 7):
            week_sessions = study_sessions[i:i+7]
            weekly_sessions.append(len(week_sessions))
        
        if len(weekly_sessions) >= 2:
            trend_direction = "increasing" if weekly_sessions[-1] > weekly_sessions[-2] else "decreasing"
            trend_strength = abs(weekly_sessions[-1] - weekly_sessions[-2]) / max(weekly_sessions[-2], 1)
        else:
            trend_direction = "stable"
            trend_strength = 0
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "weekly_average": statistics.mean(weekly_sessions) if weekly_sessions else 0,
            "consistency_trend": "improving" if trend_direction == "increasing" else "declining"
        }
    
    def _get_comparative_analysis(self, user_id: str) -> Dict:
        """Compare user's progress with similar learners"""
        if user_id not in self.user_analytics:
            return {"status": "insufficient_data"}
        
        user_data = self.user_analytics[user_id]
        
        # Simple percentile calculation (in a real system, this would use a larger dataset)
        total_sessions = len(user_data.get("study_sessions", []))
        
        if total_sessions < 10:
            percentile = 25
        elif total_sessions < 30:
            percentile = 50
        elif total_sessions < 60:
            percentile = 75
        else:
            percentile = 90
        
        return {
            "consistency_percentile": percentile,
            "progress_percentile": percentile,
            "engagement_percentile": percentile,
            "comparison_message": f"You're performing better than {percentile}% of similar learners"
        }
    
    def _update_user_analytics(self, user_id: str, analytics_result: Dict):
        """Update user's analytics data"""
        if user_id not in self.user_analytics:
            self.user_analytics[user_id] = {
                "study_sessions": [],
                "vocabulary_progress": [],
                "pronunciation_scores": [],
                "cultural_interactions": [],
                "learning_preferences": {},
                "achievements": [],
                "challenges": []
            }
        
        # Add current session data
        current_time = time.time()
        self.user_analytics[user_id]["study_sessions"].append(current_time)
        
        # Keep only last 90 days of data
        cutoff_time = current_time - (90 * 24 * 60 * 60)
        self.user_analytics[user_id]["study_sessions"] = [
            session for session in self.user_analytics[user_id]["study_sessions"]
            if session > cutoff_time
        ]
    
    def get_learning_report(self, user_id: str, report_type: str = "comprehensive") -> Dict:
        """Generate a comprehensive learning report"""
        if user_id not in self.user_analytics:
            return {"status": "new_user", "message": "Start learning to generate your first report!"}
        
        user_data = self.user_analytics[user_id]
        
        return {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_study_sessions": len(user_data.get("study_sessions", [])),
                "learning_streak": self._calculate_current_streak(user_data),
                "achievements_unlocked": len(user_data.get("achievements", [])),
                "current_level": self._determine_learning_level(user_data)
            },
            "detailed_metrics": user_data,
            "recommendations": self._generate_report_recommendations(user_data)
        }
    
    def _calculate_current_streak(self, user_data: Dict) -> int:
        """Calculate current learning streak"""
        sessions = user_data.get("study_sessions", [])
        if not sessions:
            return 0
        
        # Sort sessions by time
        sessions.sort()
        current_streak = 0
        current_date = datetime.now().date()
        
        for session_time in reversed(sessions):
            session_date = datetime.fromtimestamp(session_time).date()
            if session_date == current_date or session_date == current_date - timedelta(days=current_streak):
                current_streak += 1
                current_date = session_date
            else:
                break
        
        return current_streak
    
    def _determine_learning_level(self, user_data: Dict) -> str:
        """Determine user's learning level based on data"""
        total_sessions = len(user_data.get("study_sessions", []))
        
        if total_sessions < 10:
            return "Beginner"
        elif total_sessions < 30:
            return "Intermediate"
        elif total_sessions < 60:
            return "Advanced"
        else:
            return "Expert"
    
    def _generate_report_recommendations(self, user_data: Dict) -> List[str]:
        """Generate recommendations for the learning report"""
        recommendations = []
        
        total_sessions = len(user_data.get("study_sessions", []))
        
        if total_sessions < 5:
            recommendations.append("Start with shorter, more frequent study sessions")
        elif total_sessions < 20:
            recommendations.append("Consider increasing session length gradually")
        else:
            recommendations.append("Great progress! Consider exploring advanced topics")
        
        return recommendations

"""
Trivia Agent
Generates multiple choice trivia questions based on cultural content
"""

import json
import logging
import aiohttp
import time
from typing import Dict, List
from .base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

# Import logging system
try:
    from utils.logging import log_api_call
except ImportError:
    def log_api_call(*args, **kwargs):
        pass


class TriviaAgent(BaseAgent):
    """
    Generates 5 unique multiple choice trivia questions based on actual content cards.
    Questions test understanding of the specific content shown to the user.
    """
    
    def __init__(self, anthropic_api_key: str):
        super().__init__("Trivia", anthropic_api_key)
    
    async def _process_impl(self, input_data: Dict) -> AgentResponse:
        """
        Generates trivia questions based on content cards
        """
        try:
            country = input_data.get("country", "")
            content_cards = input_data.get("content_cards", [])
            
            logger.info(f"[Trivia] Generating 5 unique questions for {country} based on {len(content_cards)} content cards")
            
            # Generate 5 unique questions from actual content
            questions = await self._generate_unique_questions(country, content_cards)
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                data={
                    "country": country,
                    "questions": questions,
                    "total_questions": len(questions)
                },
                confidence=0.9,
                reasoning=f"Generated {len(questions)} unique trivia questions from actual content about {country}"
            )
            
        except Exception as e:
            logger.error(f"[Trivia] Error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0
            )
    
    async def _generate_unique_questions(self, country: str, content_cards: List[Dict]) -> List[Dict]:
        """Generate 5 unique questions based on actual content"""
        try:
            # Build detailed content summary for Claude
            content_summary = self._build_detailed_content_summary(content_cards)
            
            prompt = f"""
            Generate exactly 5 unique, engaging multiple-choice trivia questions based on the actual cultural content shown about {country}.
            
            IMPORTANT: Base questions ONLY on the specific content provided. Do not make up or assume information.
            
            Content Cards:
            {content_summary}
            
            Requirements:
            - Generate exactly 5 questions
            - Each question must be based on specific details from the content provided
            - Include 4 answer options (one correct, three plausible distractors)
            - Mix question types: facts about movies, news articles, songs, restaurants, attractions
            - Make questions test knowledge of the actual content shown
            - Each question should be unique and test different aspects
            
            For each question, provide:
            - question: The question text (specific to the content)
            - options: List of 4 answer options
            - correct_answer: The index (0-3) of the correct answer
            - explanation: Brief explanation
            - category: Type of content (movie, news, music, food, attraction)
            
            Respond in JSON array format with exactly 5 questions:
            [
                {{
                    "question": "What is [specific detail from content]?",
                    "options": ["Option from content", "Plausible distractor", "Another distractor", "Third distractor"],
                    "correct_answer": 0,
                    "explanation": "Because [content detail]",
                    "category": "movie/news/music/food/attraction"
                }},
                ... (exactly 4 more)
            ]
            """
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 3000,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    execution_time = time.time() - start_time
                    
                    log_api_call(
                        service="anthropic",
                        endpoint="/v1/messages",
                        method="POST",
                        request_data=data,
                        response_data={"status": response.status},
                        status_code=response.status,
                        execution_time=execution_time
                    )
                    
                    if response.status == 200:
                        result = await response.json()
                        questions_text = result["content"][0]["text"]
                        
                        # Extract JSON array
                        start_idx = questions_text.find('[')
                        end_idx = questions_text.rfind(']') + 1
                        
                        if start_idx == -1:
                            raise Exception("Could not find '[' in Claude's response")
                        
                        if end_idx <= start_idx:
                            raise Exception("Could not find ']' in Claude's response")
                        
                        try:
                            questions = json.loads(questions_text[start_idx:end_idx])
                            
                            # Ensure exactly 5 questions
                            questions = questions[:5]
                            
                            # Validate questions structure
                            if not isinstance(questions, list):
                                raise Exception("Questions is not a list")
                            
                            if len(questions) == 0:
                                raise Exception("No questions generated")
                            
                            # Validate each question has required fields
                            required_fields = ['question', 'options', 'correct_answer']
                            for i, q in enumerate(questions):
                                for field in required_fields:
                                    if field not in q:
                                        raise Exception(f"Question {i} missing required field: {field}")
                            
                            logger.info(f"[Trivia] Generated {len(questions)} unique questions from content")
                            return questions
                        except json.JSONDecodeError as je:
                            raise Exception(f"Failed to parse JSON from Claude response: {str(je)}")
                    
                    raise Exception(f"Anthropic API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"[Trivia] Error generating questions: {str(e)}")
            logger.error(f"[Trivia] Falling back to basic questions due to error: {type(e).__name__}")
        
        # Fallback: generate 5 basic questions from content
        fallback_questions = self._generate_fallback_questions(country, content_cards)
        logger.warning(f"[Trivia] Using {len(fallback_questions)} fallback questions for {country}")
        return fallback_questions
    
    def _build_detailed_content_summary(self, content_cards: List[Dict]) -> str:
        """Create detailed summary of content cards"""
        summary = []
        
        for idx, card in enumerate(content_cards):
            card_type = card.get("type", "unknown")
            
            if card_type == "movie":
                summary.append(f"""
Movie {idx + 1}:
- Title: {card.get('title', 'Unknown')}
- Description: {card.get('description', 'No description')}
                """)
            
            elif card_type == "news":
                summary.append(f"""
News Article {idx + 1}:
- Title: {card.get('title', 'Unknown')}
- Description: {card.get('description', 'No description')}
                """)
            
            elif card_type == "music":
                songs = card.get('songs', [])
                for song_idx, song in enumerate(songs):
                    summary.append(f"""
Song {song_idx + 1}:
- Name: {song.get('name', 'Unknown')}
- Artist: {song.get('artist', 'Unknown')}
                    """)
            
            elif card_type == "food":
                summary.append(f"""
Restaurant {idx + 1}:
- Name: {card.get('restaurant_name', 'Unknown')}
- Description: {card.get('description', 'No description')}
                """)
            
            elif card_type == "attraction":
                summary.append(f"""
Attraction {idx + 1}:
- Name: {card.get('name', 'Unknown')}
- Description: {card.get('description', 'No description')}
                """)
        
        return "\n".join(summary)
    
    def _generate_fallback_questions(self, country: str, content_cards: List[Dict]) -> List[Dict]:
        """Generate 5 basic fallback questions from content"""
        logger.info(f"[Trivia] Fallback: Generating basic questions for {country} from {len(content_cards)} content cards")
        questions = []
        
        # Check what content types we have
        has_movie = any(c.get('type') == 'movie' for c in content_cards)
        has_news = any(c.get('type') == 'news' for c in content_cards)
        has_music = any(c.get('type') == 'music' for c in content_cards)
        has_food = any(c.get('type') == 'food' for c in content_cards)
        has_attraction = any(c.get('type') == 'attraction' for c in content_cards)
        
        if has_movie:
            movie = next(c for c in content_cards if c.get('type') == 'movie')
            questions.append({
                "question": f"What country is this movie from: '{movie.get('title', 'Unknown')}'?",
                "options": [country, "Italy", "France", "Spain"],
                "correct_answer": 0,
                "explanation": f"This movie is from {country}.",
                "category": "movie"
            })
        
        if has_news:
            news = next(c for c in content_cards if c.get('type') == 'news')
            questions.append({
                "question": f"Which country do these news articles discuss?",
                "options": [country, "Germany", "Brazil", "Japan"],
                "correct_answer": 0,
                "explanation": f"These articles discuss {country}.",
                "category": "news"
            })
        
        if has_music:
            music_card = next(c for c in content_cards if c.get('type') == 'music')
            songs = music_card.get('songs', [])
            if songs:
                song = songs[0]
                questions.append({
                    "question": f"What type of music is popular in {country}?",
                    "options": [song.get('name', 'Local music'), "Classical", "Electronic", "Jazz"],
                    "correct_answer": 0,
                    "explanation": f"'{song.get('name', 'Local music')}' is popular in {country}.",
                    "category": "music"
                })
        
        if has_food:
            questions.append({
                "question": f"What type of cuisine is featured from {country}?",
                "options": ["Traditional", "Fast food", "Fusion", "Western"],
                "correct_answer": 0,
                "explanation": f"Traditional cuisine is featured from {country}.",
                "category": "food"
            })
        
        if has_attraction:
            questions.append({
                "question": f"Which type of site would you visit in {country}?",
                "options": ["Cultural landmark", "Shopping mall", "Theme park", "Sports arena"],
                "correct_answer": 0,
                "explanation": f"Cultural landmarks are featured in {country}.",
                "category": "attraction"
            })
        
        # Fill remaining slots with general questions
        while len(questions) < 5:
            questions.append({
                "question": f"What makes {country}'s culture unique?",
                "options": ["All of its aspects", "Only food", "Only music", "Only history"],
                "correct_answer": 0,
                "explanation": f"All aspects contribute to {country}'s unique culture.",
                "category": "general"
            })
        
        return questions[:5]

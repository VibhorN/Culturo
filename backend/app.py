import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import json
import asyncio
from datetime import datetime
import logging
from integrations import (
    DeepgramIntegration, VapiIntegration, SpotifyIntegration,
    NewsAPIIntegration, RedditIntegration, AnthropicIntegration
)
from core.orchestrator import AgentOrchestrator

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys and Configuration
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
VAPI_API_KEY = os.getenv('VAPI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
LETTA_API_KEY = os.getenv('LETTA_API_KEY')
ARIZE_API_KEY = os.getenv('ARIZE_API_KEY')
TRIPADVISOR_API_KEY = os.getenv('TRIPADVISOR_API_KEY')

# Initialize API integrations
deepgram = DeepgramIntegration(DEEPGRAM_API_KEY) if DEEPGRAM_API_KEY else None
vapi = VapiIntegration(VAPI_API_KEY) if VAPI_API_KEY else None
spotify = SpotifyIntegration(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET) if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET else None
news_api = NewsAPIIntegration(NEWS_API_KEY) if NEWS_API_KEY else None
reddit = RedditIntegration(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, "WorldWise-CulturalBot/1.0") if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET else None
claude = AnthropicIntegration(ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# Make Anthropic client available globally for Arize evaluations
try:
    import anthropic
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
except ImportError:
    anthropic_client = None

# Initialize Arize Agent Evaluations Project
try:
    from integrations.arize_agent_evaluations import arize_agent_evaluations
    if arize_agent_evaluations.enabled:
        logger.info("Arize Agent Evaluations Project initialized successfully")
    else:
        logger.warning("Arize Agent Evaluations Project not enabled")
except Exception as e:
    logger.warning(f"Failed to initialize Arize Agent Evaluations Project: {str(e)}")

# Initialize Agent Orchestrator with Anthropic API
try:
    agent_orchestrator = AgentOrchestrator(
        ANTHROPIC_API_KEY,
        NEWS_API_KEY,
        SPOTIFY_CLIENT_ID,
        SPOTIFY_CLIENT_SECRET,
        TRIPADVISOR_API_KEY
    )
    # Pass the Anthropic client to the orchestrator for evaluations
    if agent_orchestrator and anthropic_client:
        agent_orchestrator.anthropic_client = anthropic_client
    logger.info("Agent orchestrator initialized with Anthropic API and all integrations")
except Exception as e:
    logger.warning(f"Failed to initialize agent orchestrator: {str(e)}")
    agent_orchestrator = None

class CulturalDataAggregator:
    """Main class for aggregating cultural data from multiple APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WorldWise-CulturalBot/1.0'
        })
    
    async def get_cultural_data(self, country, language="en"):
        """Main method to gather comprehensive cultural data"""
        try:
            # Parallel API calls for efficiency
            tasks = [
                self.get_government_info(country),
                self.get_news_data(country),
                self.get_music_data(country),
                self.get_food_data(country),
                self.get_slang_data(country),
                self.get_festivals_data(country)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            cultural_data = {
                "country": country,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "government": results[0] if not isinstance(results[0], Exception) else None,
                "news": results[1] if not isinstance(results[1], Exception) else None,
                "music": results[2] if not isinstance(results[2], Exception) else None,
                "food": results[3] if not isinstance(results[3], Exception) else None,
                "slang": results[4] if not isinstance(results[4], Exception) else None,
                "festivals": results[5] if not isinstance(results[5], Exception) else None
            }
            
            return cultural_data
            
        except Exception as e:
            logger.error(f"Error in get_cultural_data: {str(e)}")
            return {"error": str(e)}
    
    async def get_government_info(self, country):
        """Get government and historical information from Wikipedia"""
        try:
            import wikipedia
            wikipedia.set_lang("en")
            
            # Search for country information
            search_results = wikipedia.search(f"{country} government")
            if search_results:
                page = wikipedia.page(search_results[0])
                
                return {
                    "title": page.title,
                    "summary": page.summary[:500] + "..." if len(page.summary) > 500 else page.summary,
                    "url": page.url,
                    "categories": page.categories[:10]  # Limit categories
                }
        except Exception as e:
            logger.error(f"Error getting government info: {str(e)}")
            return None
    
    async def get_news_data(self, country):
        """Get current news from NewsAPI"""
        try:
            if news_api:
                articles = await news_api.get_cultural_news(country)
                if articles:
                    return {
                        "articles": articles,
                        "total_results": len(articles),
                        "source": "NewsAPI"
                    }
            
            # Fallback to sample news data
            sample_news = {
                "japan": [
                    {"title": "Cherry Blossom Season Begins in Tokyo", "description": "The annual hanami season brings cultural celebrations across Japan."},
                    {"title": "Traditional Tea Ceremony Gains Global Interest", "description": "More international visitors are learning about Japanese tea culture."}
                ],
                "korea": [
                    {"title": "K-Pop Continues Global Expansion", "description": "Korean music and culture reach new audiences worldwide."},
                    {"title": "Korean Cuisine Gains Michelin Recognition", "description": "Traditional Korean dishes receive international acclaim."}
                ]
            }
            
            country_lower = country.lower()
            articles = sample_news.get(country_lower, [
                {"title": f"Cultural Events in {country}", "description": "Local traditions and celebrations continue to thrive."}
            ])
            
            return {
                "articles": articles,
                "total_results": len(articles),
                "source": "Cultural database"
            }
            
        except Exception as e:
            logger.error(f"Error getting news data: {str(e)}")
            return None
    
    async def get_music_data(self, country):
        """Get trending music from Spotify"""
        try:
            if spotify:
                playlists = await spotify.search_playlists(country, limit=5)
                if playlists:
                    return {
                        "playlists": playlists,
                        "country": country,
                        "source": "Spotify API"
                    }
            
            # Fallback to sample data
            sample_foods = {
                "japan": ["Fujii Kaze", "Ado", "Yoasobi", "King Gnu", "Aimyon"],
                "korea": ["BTS", "BLACKPINK", "IU", "NewJeans", "LE SSERAFIM"],
                "italy": ["Laura Pausini", "Eros Ramazzotti", "Tiziano Ferro", "Marco Mengoni", "Francesco Gabbani"],
                "mexico": ["Bad Bunny", "J Balvin", "Maluma", "Shakira", "Karol G"],
                "india": ["A.R. Rahman", "Lata Mangeshkar", "Kishore Kumar", "Arijit Singh", "Neha Kakkar"]
            }
            
            country_lower = country.lower()
            artists = sample_foods.get(country_lower, ["Local artists", "Popular musicians"])
            
            return {
                "country": country,
                "popular_artists": artists,
                "source": "Cultural database"
            }
            
        except Exception as e:
            logger.error(f"Error getting music data: {str(e)}")
            return None
    
    async def get_food_data(self, country):
        """Get food and restaurant data from TripAdvisor API"""
        try:
            # For demo purposes, return sample food data
            # In production, integrate with TripAdvisor API
            sample_foods = {
                "japan": ["sushi", "ramen", "tempura", "okonomiyaki", "takoyaki"],
                "korea": ["kimchi", "bulgogi", "bibimbap", "korean bbq", "tteokbokki"],
                "italy": ["pizza", "pasta", "risotto", "gelato", "tiramisu"],
                "mexico": ["tacos", "burritos", "quesadillas", "guacamole", "churros"],
                "india": ["curry", "naan", "biryani", "samosa", "tandoori"]
            }
            
            country_lower = country.lower()
            foods = sample_foods.get(country_lower, ["local cuisine", "traditional dishes"])
            
            return {
                "country": country,
                "popular_foods": foods,
                "etiquette_tips": [
                    "Try local specialties",
                    "Ask about ingredients if you have allergies",
                    "Respect local dining customs"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting food data: {str(e)}")
            return None
    
    async def get_slang_data(self, country):
        """Get slang and cultural expressions"""
        try:
            # Sample slang data - in production, integrate with Reddit API
            sample_slang = {
                "japan": [
                    {"term": "やばい (yabai)", "meaning": "That's crazy!", "usage": "Can be good or bad"},
                    {"term": "かわいい (kawaii)", "meaning": "Cute", "usage": "Very common expression"},
                    {"term": "すごい (sugoi)", "meaning": "Amazing", "usage": "Positive exclamation"}
                ],
                "korea": [
                    {"term": "대박 (daebak)", "meaning": "Awesome!", "usage": "Very popular slang"},
                    {"term": "헐 (heol)", "meaning": "OMG", "usage": "Expression of surprise"},
                    {"term": "짱 (jjang)", "meaning": "The best", "usage": "Something excellent"}
                ]
            }
            
            country_lower = country.lower()
            slang = sample_slang.get(country_lower, [
                {"term": "local expression", "meaning": "Check local sources", "usage": "Learn from locals"}
            ])
            
            return {
                "country": country,
                "slang_expressions": slang,
                "source": "Cultural database"
            }
            
        except Exception as e:
            logger.error(f"Error getting slang data: {str(e)}")
            return None
    
    async def get_festivals_data(self, country):
        """Get festivals and cultural events"""
        try:
            # Sample festival data - in production, integrate with event APIs
            sample_festivals = {
                "japan": ["Hanami (Cherry Blossom)", "Obon Festival", "Tanabata", "Golden Week"],
                "korea": ["Chuseok", "Seollal", "Buddha's Birthday", "Dano Festival"],
                "italy": ["Carnevale", "Festa della Repubblica", "Ferragosto", "Christmas"],
                "mexico": ["Día de los Muertos", "Cinco de Mayo", "Independence Day", "Guadalupe Day"],
                "india": ["Diwali", "Holi", "Eid", "Christmas", "Dussehra"]
            }
            
            country_lower = country.lower()
            festivals = sample_festivals.get(country_lower, ["Local festivals", "Cultural celebrations"])
            
            return {
                "country": country,
                "major_festivals": festivals,
                "cultural_notes": [
                    "Respect local traditions",
                    "Learn about festival meanings",
                    "Participate respectfully"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting festivals data: {str(e)}")
            return None

# Initialize the cultural data aggregator
cultural_aggregator = CulturalDataAggregator()

@app.route('/api/cultural-data/<country>', methods=['GET'])
async def get_cultural_data_endpoint(country):
    """Main endpoint to get comprehensive cultural data for a country"""
    try:
        language = request.args.get('language', 'en')
        data = await cultural_aggregator.get_cultural_data(country, language)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in cultural data endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice/transcribe', methods=['POST'])
async def transcribe_audio():
    """Transcribe audio using Deepgram"""
    try:
        if not deepgram:
            return jsonify({"error": "Deepgram API key not configured"}), 500
        
        # Get audio file from request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'auto')
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Get content type from the uploaded file with better detection
        content_type = audio_file.content_type or 'audio/webm'
        
        # If content type is generic, try to detect from filename
        if content_type == 'application/octet-stream' or not content_type:
            filename = audio_file.filename or ''
            if filename.endswith('.mp4') or filename.endswith('.m4a'):
                content_type = 'audio/mp4'
            elif filename.endswith('.wav'):
                content_type = 'audio/wav'
            elif filename.endswith('.webm'):
                content_type = 'audio/webm'
            else:
                content_type = 'audio/webm'  # Default fallback
        
        logger.info(f"Processing audio: {len(audio_data)} bytes, content_type: {content_type}, language: {language}")
        
        # Transcribe using Deepgram
        result = await deepgram.transcribe_audio(audio_data, language, content_type)
        
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Transcription failed"}), 500
        
    except Exception as e:
        logger.error(f"Error in transcription: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice/synthesize', methods=['POST'])
async def synthesize_speech():
    """Synthesize speech using Vapi"""
    try:
        logger.info("Starting speech synthesis request")
        
        # Check if VAPI is configured
        if not vapi:
            logger.error("VAPI API key not configured")
            return jsonify({"error": "Vapi API key not configured"}), 500
        
        # Validate request data
        data = request.get_json()
        if not data:
            logger.error("No JSON data provided")
            return jsonify({"error": "No JSON data provided"}), 400
        
        text = data.get('text', '')
        language = data.get('language', 'en')
        voice = data.get('voice', 'alloy')
        
        # Validate text input
        if not text or not text.strip():
            logger.error("Empty text provided for synthesis")
            return jsonify({"error": "Text is required for speech synthesis"}), 400
        
        logger.info(f"Synthesizing speech: text='{text[:50]}...', language='{language}', voice='{voice}'")
        
        # Synthesize using Vapi
        try:
            result = await vapi.synthesize_speech(text, voice, language)
        except Exception as vapi_error:
            logger.error(f"VAPI synthesis error: {str(vapi_error)}")
            return jsonify({
                "error": "Speech synthesis failed", 
                "details": str(vapi_error),
                "fallback_to_browser": True,
                "text": text
            }), 500
        
        if result:
            logger.info(f"Speech synthesis successful: {result.get('message', 'Unknown')}")
            return jsonify(result)
        else:
            logger.error("VAPI returned None result")
            return jsonify({
                "error": "Speech synthesis failed - no result from VAPI",
                "fallback_to_browser": True,
                "text": text
            }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in speech synthesis: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error during speech synthesis",
            "details": str(e),
            "fallback_to_browser": True,
            "text": data.get('text', '') if 'data' in locals() else ''
        }), 500

@app.route('/api/claude/reason', methods=['POST'])
async def claude_reasoning():
    """Use Claude for cultural reasoning and synthesis"""
    try:
        if not claude:
            return jsonify({"error": "Anthropic API key not configured"}), 500
        
        data = request.get_json()
        cultural_data = data.get('cultural_data', {})
        user_query = data.get('query', '')
        
        # Use Claude to synthesize cultural data
        synthesis = await claude.synthesize_cultural_data(cultural_data, user_query)
        
        if synthesis:
            return jsonify(synthesis)
        else:
            return jsonify({"error": "Claude synthesis failed"}), 500
        
    except Exception as e:
        logger.error(f"Error in Claude reasoning: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/process', methods=['POST'])
async def agent_process():
    """
    Main agentic workflow endpoint
    Processes user input through multiple specialized agents
    """
    try:
        if not agent_orchestrator:
            return jsonify({"error": "Agent system not configured. Please set ANTHROPIC_API_KEY"}), 500
        
        data = request.get_json()
        
        # Extract user input
        user_input = {
            "user_id": data.get('user_id', 'default'),
            "query": data.get('query', ''),
            "text": data.get('text', ''),
            "language": data.get('language', 'en'),
            "audio_confidence": data.get('audio_confidence', 1.0),
            "cultural_data": data.get('cultural_data', {}),
            "session_data": data.get('session_data', {}),
            "input_type": data.get('input_type', 'text'),  # 'voice' or 'text'
            "voice_context": {
                "is_voice_input": data.get('input_type') == 'voice',
                "audio_confidence": data.get('audio_confidence', 1.0),
                "transcription_quality": data.get('audio_confidence', 1.0)
            }
        }
        
        # Process through agent workflow
        result = await agent_orchestrator.process_input(user_input)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in agent processing: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/correct-language', methods=['POST'])
async def agent_correct_language():
    """
    Language correction endpoint using the LanguageCorrectionAgent
    """
    try:
        if not agent_orchestrator:
            return jsonify({"error": "Agent system not configured"}), 500
        
        data = request.get_json()
        
        response = await agent_orchestrator.language_correction.process({
            "text": data.get('text', ''),
            "target_language": data.get('target_language', 'en'),
            "native_language": data.get('native_language', 'en'),
            "audio_confidence": data.get('audio_confidence', 1.0)
        })
        
        return jsonify({
            "status": response.status,
            "corrections": response.data,
            "confidence": response.confidence
        })
        
    except Exception as e:
        logger.error(f"Error in language correction: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/cultural-insights', methods=['POST'])
async def agent_cultural_insights():
    """
    Get cultural insights using the CulturalContextAgent
    """
    try:
        if not agent_orchestrator:
            return jsonify({"error": "Agent system not configured"}), 500
        
        data = request.get_json()
        
        response = await agent_orchestrator.cultural_context.process({
            "country": data.get('country', ''),
            "topic": data.get('topic', 'general'),
            "cultural_data": data.get('cultural_data', {}),
            "query": data.get('query', '')
        })
        
        return jsonify({
            "status": response.status,
            "insights": response.data,
            "confidence": response.confidence
        })
        
    except Exception as e:
        logger.error(f"Error getting cultural insights: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/translate', methods=['POST'])
async def agent_translate():
    """
    Translation endpoint using the TranslationAgent
    """
    try:
        if not agent_orchestrator:
            return jsonify({"error": "Agent system not configured"}), 500
        
        data = request.get_json()
        
        response = await agent_orchestrator.translation.process({
            "text": data.get('text', ''),
            "source_language": data.get('source_language', 'auto'),
            "target_language": data.get('target_language', 'en'),
            "context": data.get('context', '')
        })
        
        return jsonify({
            "status": response.status,
            "translation": response.data,
            "confidence": response.confidence
        })
        
    except Exception as e:
        logger.error(f"Error in translation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "agents_available": agent_orchestrator is not None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
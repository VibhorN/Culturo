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
    NewsAPIIntegration, RedditIntegration, ClaudeIntegration
)

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

# Initialize API integrations
deepgram = DeepgramIntegration(DEEPGRAM_API_KEY) if DEEPGRAM_API_KEY else None
vapi = VapiIntegration(VAPI_API_KEY) if VAPI_API_KEY else None
spotify = SpotifyIntegration(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET) if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET else None
news_api = NewsAPIIntegration(NEWS_API_KEY) if NEWS_API_KEY else None
reddit = RedditIntegration(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET) if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET else None
claude = ClaudeIntegration(ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

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
        language = request.form.get('language', 'en-US')
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Transcribe using Deepgram
        result = await deepgram.transcribe_audio(audio_data, language)
        
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
        if not vapi:
            return jsonify({"error": "Vapi API key not configured"}), 500
        
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'en')
        voice = data.get('voice', 'alloy')
        
        # Synthesize using Vapi
        result = await vapi.synthesize_speech(text, voice, language)
        
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Speech synthesis failed"}), 500
        
    except Exception as e:
        logger.error(f"Error in speech synthesis: {str(e)}")
        return jsonify({"error": str(e)}), 500

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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
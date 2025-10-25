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
    SpotifyIntegration, NewsAPIIntegration, RedditIntegration, AnthropicIntegration
)
from agents import AgentOrchestrator

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys and Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
LETTA_API_KEY = os.getenv('LETTA_API_KEY')
ARIZE_API_KEY = os.getenv('ARIZE_API_KEY')

# Initialize API integrations
spotify = SpotifyIntegration(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET) if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET else None
news_api = NewsAPIIntegration(NEWS_API_KEY) if NEWS_API_KEY else None
reddit = RedditIntegration(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT) if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET and REDDIT_USER_AGENT else None
claude = AnthropicIntegration(ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# Initialize Agent Orchestrator with Anthropic API
try:
    agent_orchestrator = AgentOrchestrator(ANTHROPIC_API_KEY)
    logger.info("Agent orchestrator initialized with Anthropic API")
except Exception as e:
    logger.error(f"Failed to initialize agent orchestrator: {str(e)}")
    agent_orchestrator = None

# Cultural Data Aggregator Class
class CulturalDataAggregator:
    """Aggregates cultural data from multiple sources"""
    
    def __init__(self):
        self.spotify = spotify
        self.news_api = news_api
        self.reddit = reddit
        self.claude = claude
    
    async def get_cultural_data(self, country, language="en"):
        """Get comprehensive cultural data for a country"""
        try:
            data = {
                "country": country,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "government_info": self.get_government_info(country),
                "news_data": self.get_news_data(country),
                "music_data": await self.get_music_data(country),
                "food_data": await self.get_food_data(country),
                "slang_data": await self.get_slang_data(country),
                "festivals_data": await self.get_festivals_data(country)
            }
            return data
        except Exception as e:
            logger.error(f"Error getting cultural data: {str(e)}")
            return {"error": str(e)}
    
    def get_government_info(self, country):
        """Get government and political information"""
        try:
            # Use Wikipedia or other sources for government info
            return {
                "source": "Wikipedia",
                "title": f"Government of {country}",
                "summary": f"Information about the government structure of {country}"
            }
        except Exception as e:
            logger.error(f"Error getting government info: {str(e)}")
            return None
    
    def get_news_data(self, country):
        """Get current news for the country"""
        try:
            if self.news_api:
                return self.news_api.get_headlines(country)
            else:
                return {
                    "source": "Mock data",
                    "headlines": [f"Latest news from {country}", f"Cultural events in {country}"]
                }
        except Exception as e:
            logger.error(f"Error getting news data: {str(e)}")
            return None
    
    async def get_music_data(self, country):
        """Get music and cultural data"""
        try:
            if self.spotify:
                return await self.spotify.search_playlists(country)
            else:
                return {
                    "source": "Mock data",
                    "playlists": [f"Popular music from {country}", f"Traditional {country} music"]
                }
        except Exception as e:
            logger.error(f"Error getting music data: {str(e)}")
            return None
    
    async def get_food_data(self, country):
        """Get food and cuisine information"""
        try:
            return {
                "source": "Cultural database",
                "popular_foods": [f"Traditional {country} dish 1", f"Traditional {country} dish 2"],
                "cuisine_type": f"{country} cuisine",
                "description": f"Information about {country} food culture"
            }
        except Exception as e:
            logger.error(f"Error getting food data: {str(e)}")
            return None
    
    async def get_slang_data(self, country):
        """Get slang and colloquial expressions"""
        try:
            if self.reddit:
                return await self.reddit.search_slang(country)
            else:
                return {
                    "source": "Mock data",
                    "slang_expressions": [
                        {"term": f"{country} slang 1", "meaning": "Local expression"},
                        {"term": f"{country} slang 2", "meaning": "Common phrase"}
                    ]
                }
        except Exception as e:
            logger.error(f"Error getting slang data: {str(e)}")
            return None
    
    async def get_festivals_data(self, country):
        """Get festivals and cultural events"""
        try:
            return {
                "source": "Cultural database",
                "major_festivals": [f"{country} Festival 1", f"{country} Festival 2"],
                "cultural_events": [f"Traditional {country} celebration"],
                "description": f"Cultural festivals and events in {country}"
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

@app.route('/api/claude/reason', methods=['POST'])
def claude_reasoning():
    """Use Claude for cultural reasoning and synthesis"""
    try:
        if not claude:
            return jsonify({"error": "Anthropic API key not configured"}), 500
        
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Use Claude for reasoning
        response = claude.generate_response(prompt)
        
        if response:
            return jsonify(response)
        else:
            return jsonify({"error": "Failed to get response from Claude"}), 500
        
    except Exception as e:
        logger.error(f"Error in Claude reasoning: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/process', methods=['POST'])
async def agent_process():
    """Main agent processing endpoint"""
    try:
        if not agent_orchestrator:
            return jsonify({"error": "Agent orchestrator not initialized"}), 500
        
        data = request.get_json()
        user_input = data.get('query', '')
        
        if not user_input:
            return jsonify({"error": "No query provided"}), 400
        
        # Process with agent orchestrator
        result = await agent_orchestrator.process_input({
            "query": user_input,
            "user_id": data.get('user_id', 'anonymous'),
            "context": data.get('context', {})
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in agent processing: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/correct-language', methods=['POST'])
def agent_correct_language():
    """Language correction endpoint"""
    try:
        if not agent_orchestrator:
            return jsonify({"error": "Agent orchestrator not initialized"}), 500
        
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Use language correction agent
        result = agent_orchestrator.language_correction.process({
            "text": text,
            "language": language
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in language correction: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/cultural-insights', methods=['POST'])
def agent_cultural_insights():
    """Cultural insights endpoint"""
    try:
        if not agent_orchestrator:
            return jsonify({"error": "Agent orchestrator not initialized"}), 500
        
        data = request.get_json()
        query = data.get('query', '')
        country = data.get('country', '')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Use cultural context agent
        result = agent_orchestrator.cultural_context.process({
            "query": query,
            "country": country
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in cultural insights: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/translate', methods=['POST'])
def agent_translate():
    """Translation endpoint"""
    try:
        if not agent_orchestrator:
            return jsonify({"error": "Agent orchestrator not initialized"}), 500
        
        data = request.get_json()
        text = data.get('text', '')
        target_language = data.get('target_language', 'en')
        source_language = data.get('source_language', 'auto')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Use translation agent
        result = agent_orchestrator.translation.process({
            "text": text,
            "source_language": source_language,
            "target_language": target_language
        })
        
        return jsonify(result)
        
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
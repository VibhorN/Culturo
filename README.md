# 🌍 WorldWise - Agentic AI Cultural Immersion Companion

> **"Duolingo meets ChatGPT — but instead of just learning a language, you *live* the culture."**

WorldWise is a voice-based AI agent that helps you immerse yourself in any country's culture, combining language, history, government, music, food, slang, and social insights in real time.

## 🚀 Features

### 🗣️ Voice Interface
- **Multilingual Speech Recognition** - Powered by Deepgram
- **Natural Voice Synthesis** - Powered by Vapi
- **Real-time Conversation** - Full duplex voice interaction

### 🧠 AI-Powered Cultural Intelligence
- **Claude AI Reasoning** - Anthropic's Claude for cultural synthesis
- **Multi-API Orchestration** - Postman Flows for intelligent data aggregation
- **Cultural Memory** - Letta integration for personalized learning

### 🌐 Comprehensive Cultural Data
- **Government & History** - Wikipedia/Wikidata integration
- **Current News** - NewsAPI for real-time cultural events
- **Music & Artists** - Spotify API for trending local music
- **Food & Cuisine** - TripAdvisor/Yelp for local dining
- **Slang & Expressions** - Reddit API for authentic local language
- **Festivals & Events** - Cultural calendar and traditions

### 📊 Observability & Analytics
- **Arize Phoenix** - AI reasoning traceability and evaluation
- **Performance Metrics** - Response time, accuracy, engagement tracking
- **User Progress** - Learning journey and cultural immersion tracking

## 🏗️ Architecture

```
[User Voice Input]
   ↓
[Deepgram STT] → [Cultural Data Aggregation]
   ↓
[Claude AI Agent] → [Multi-API Orchestration]
   ├── Wikipedia/Wikidata (Government/History)
   ├── NewsAPI (Current Events)
   ├── Spotify (Music Trends)
   ├── Reddit (Slang/Culture)
   ├── TripAdvisor (Food/Attractions)
   └── Google Maps (Landmarks/Events)
   ↓
[Claude Synthesis] → [Cultural Micro-lesson]
   ↓
[Vapi TTS] → [Voice Response]
   ↓
[Arize Analytics] → [Performance Tracking]
```

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **Deepgram** - Multilingual speech-to-text
- **Vapi** - Voice interface and TTS
- **Anthropic Claude** - AI reasoning and synthesis
- **Spotify API** - Music data
- **NewsAPI** - Current news
- **Reddit API** - Cultural insights
- **Wikipedia API** - Historical/government data

### Frontend
- **React 19** - Modern UI framework
- **Styled Components** - CSS-in-JS styling
- **Framer Motion** - Smooth animations
- **React Speech Kit** - Voice interface
- **Axios** - API communication

### Infrastructure
- **Postman Flows** - API orchestration
- **Letta** - Memory and personalization
- **Arize Phoenix** - Observability
- **Fetch.ai** - Agent deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- API keys for all services (see Configuration)

### Backend Setup

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp env.example .env
# Edit .env with your API keys
```

4. **Run the Flask server:**
```bash
python app.py
```

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm start
```

4. **Open your browser:**
```
http://localhost:3000
```

## 🔑 Configuration

### Required API Keys

Create a `.env` file in the backend directory with the following keys:

```env
# Voice & AI
DEEPGRAM_API_KEY=your_deepgram_api_key
VAPI_API_KEY=your_vapi_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Music & Media
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
NEWS_API_KEY=your_news_api_key

# Social & Cultural Data
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Memory & Analytics
LETTA_API_KEY=your_letta_api_key
ARIZE_API_KEY=your_arize_api_key
```

### Getting API Keys

1. **Deepgram** - [Sign up](https://deepgram.com/) for speech-to-text
2. **Vapi** - [Get API key](https://vapi.ai/) for voice synthesis
3. **Anthropic** - [Claude API](https://console.anthropic.com/) for AI reasoning
4. **Spotify** - [Developer Dashboard](https://developer.spotify.com/) for music data
5. **NewsAPI** - [Free tier](https://newsapi.org/) for news data
6. **Reddit** - [Reddit API](https://www.reddit.com/prefs/apps) for cultural insights

## 💬 Example Usage

### Voice Interaction
```
User: "Hey, I'm flying to Tokyo next week. Can you teach me the basics?"

WorldWise: "Sure! In Japan, a polite greeting is 'Hajimemashite' — it means 'Nice to meet you.'
🇯🇵 The current government is a constitutional monarchy led by Prime Minister Fumio Kishida.
🍣 For food, locals love ramen alleys in Shinjuku and okonomiyaki in Osaka.
🎵 Here's what's trending on Spotify Japan: Fujii Kaze's 'Workin' Hard'.
🗣️ Slang tip: saying 'Yabai!' means 'That's crazy!' — good or bad.
Want to hear about festivals or how to behave at dinner?"
```

### Cultural Data Response
```json
{
  "country": "Japan",
  "government": {
    "title": "Government of Japan",
    "summary": "Constitutional monarchy with parliamentary democracy...",
    "url": "https://en.wikipedia.org/wiki/Government_of_Japan"
  },
  "music": {
    "playlists": [
      {
        "name": "Tokyo Rising",
        "description": "Latest hits from Japan",
        "tracks": {"total": 50}
      }
    ]
  },
  "food": {
    "popular_foods": ["sushi", "ramen", "tempura", "okonomiyaki"],
    "etiquette_tips": ["Try local specialties", "Respect dining customs"]
  },
  "slang": {
    "slang_expressions": [
      {
        "term": "やばい (yabai)",
        "meaning": "That's crazy!",
        "usage": "Can be good or bad"
      }
    ]
  }
}
```

## 🎯 Key Features Explained

### 1. Voice-First Interface
- **Natural Conversation**: Speak naturally, get cultural insights
- **Multilingual Support**: Works in multiple languages
- **Real-time Processing**: Instant cultural data aggregation

### 2. Cultural Intelligence
- **Comprehensive Data**: Government, history, music, food, slang
- **Real-time Updates**: Current news and trending topics
- **Authentic Sources**: Reddit, Wikipedia, official APIs

### 3. Personalized Learning
- **Memory System**: Remembers your interests and progress
- **Adaptive Content**: Adjusts to your learning style
- **Cultural Quizzes**: Interactive learning experiences

### 4. Observability
- **AI Tracing**: Track AI reasoning and decision-making
- **Performance Metrics**: Monitor accuracy and user engagement
- **Continuous Improvement**: Data-driven enhancements

## 🔧 Development

### Project Structure
```
lingua-cal-hacks/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── integrations.py     # API integration classes
│   ├── requirements.txt    # Python dependencies
│   └── env.example        # Environment configuration
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Styling
│   │   └── index.js       # Entry point
│   ├── package.json       # Node dependencies
│   └── public/            # Static assets
└── README.md              # This file
```

### API Endpoints

#### Cultural Data
- `GET /api/cultural-data/<country>` - Get comprehensive cultural data
- `POST /api/claude/reason` - AI-powered cultural synthesis

#### Voice Interface
- `POST /api/voice/transcribe` - Speech-to-text conversion
- `POST /api/voice/synthesize` - Text-to-speech synthesis

#### Health & Monitoring
- `GET /api/health` - System health check

### Adding New Integrations

1. **Create integration class** in `integrations.py`
2. **Add API key** to environment configuration
3. **Update CulturalDataAggregator** to use new integration
4. **Test integration** with sample data

Example:
```python
class NewAPIIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
    
    async def get_data(self, country):
        # Implementation here
        pass
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
```bash
# Set production environment variables
export FLASK_ENV=production
export DATABASE_URL=postgresql://...
export REDIS_URL=redis://...
```

2. **Backend Deployment**
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t worldwise-backend .
docker run -p 5000:5000 worldwise-backend
```

3. **Frontend Deployment**
```bash
# Build for production
npm run build

# Serve with nginx or similar
# Deploy build/ directory to CDN
```

### Scaling Considerations

- **Database**: PostgreSQL for user data and cultural cache
- **Caching**: Redis for API response caching
- **CDN**: CloudFront for static assets
- **Monitoring**: Arize Phoenix for AI observability
- **Load Balancing**: Multiple backend instances

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Submit a pull request**

### Development Guidelines

- **Code Style**: Follow PEP 8 for Python, ESLint for JavaScript
- **Testing**: Write unit tests for new features
- **Documentation**: Update README for new integrations
- **API Keys**: Never commit API keys to version control

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Anthropic** - Claude AI for cultural reasoning
- **Deepgram** - Multilingual speech recognition
- **Vapi** - Voice interface platform
- **Spotify** - Music data API
- **NewsAPI** - News aggregation
- **Reddit** - Cultural insights
- **Wikipedia** - Historical data
- **Arize** - AI observability platform

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@worldwise.ai

---

**Built with ❤️ for cultural understanding and global connection.**
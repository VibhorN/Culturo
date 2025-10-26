# Cultura: Your Cultural Immersion Platformura

Cultura is a comprehensive cultural immersion application that provides rich, **real-time** content about countries including movies, news, music, food, attractions, and interactive trivia. All data is aggregated from multiple APIs and presented in an immersive UI

## Features

### Voice Interface (Vapi + Deepgram)
- Speech recognition using Deepgram for voice input
- Natural voice synthesis for responses
- Real-time voice conversation about cultures and countries

### Content Feed (News API, TripAdvisor API, Spotify API)
- Movie cards with embedded YouTube trailers
- News cards with current events and articles
- Music cards with popular songs and Spotify integration
- Food cards with local cuisine and restaurants
- Attraction cards with landmarks and cultural sites

### Interactive Trivia
- Daily cultural quizzes for selected countries
- Multiple choice questions with immediate feedback
- Adaptive learning system that re-queues incorrect answers
- Completion tracking and progress monitoring

## Architecture

```
[User Selects Country]
   ↓
[Loading Screen with Country Facts]
   ↓
[Backend Orchestration] → [Multi-API Data Aggregation]
   ├── TMDB (Movie Trailers)
   ├── NewsAPI (Current Events)
   ├── Spotify (Music Playlists)
   ├── TripAdvisor (Food & Attractions)
   └── LLM Agents (Trivia Generation)
   ↓
[Country-Themed Snapshot Page]
   ├── Content Feed (Movies, News, Food, Attractions)
   ├── Interactive Trivia Panel
   └── Voice Assistant Interface
```

## Tech Stack

### Backend
- Flask - Python web framework
- Python 3.8+ - Async/await support
- Deepgram - Speech-to-text transcription
- Vapi - Voice assistant and TTS synthesis
- Anthropic Claude - AI reasoning and content generation
- TMDB - Movie trailer data
- Spotify API - Music playlists and trending songs
- NewsAPI - Current events and news
- TripAdvisor API - Food and restaurant data
- Agent-based architecture for content aggregation

### Frontend
- React 
- Styled Components - CSS-in-JS styling
- Framer Motion - Smooth animations and transitions
- Axios

### Infrastructure
- Agent Orchestrator - Coordinates multiple specialized agents
- Deepgram Integration - Real-time speech recognition
- Vapi Integration - Voice assistant capabilities
- TMDB Integration - Movie and trailer data
- Spotify Integration - Music discovery
- NewsAPI Integration - Current events

## Quick Start

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

## Configuration

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
TMDB_API_KEY=your_tmdb_api_key

# Social & Cultural Data
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Tourism & Attractions
TRIPADVISOR_API_KEY=your_tripadvisor_api_key

# Memory & Analytics
LETTA_API_KEY=your_letta_api_key
```

### Getting API Keys

1. Deepgram - Sign up at https://deepgram.com/ for speech-to-text
2. Vapi - Get API key at https://vapi.ai/ for voice synthesis
3. Anthropic - Claude API at https://console.anthropic.com/ for AI reasoning
4. Spotify - Developer Dashboard at https://developer.spotify.com/ for music data
5. NewsAPI - Free tier at https://newsapi.org/ for news data
6. TMDB - Get API key at https://www.themoviedb.org/settings/api for movie trailers
7. Reddit - Reddit API at https://www.reddit.com/prefs/apps for cultural insights
8. TripAdvisor - Developer portal for food and attraction data

## Example Usage

### Voice Interaction
```
User: "Hey, I'm flying to Tokyo next week. Can you teach me the basics?"

Cultura: "Sure! In Japan, a polite greeting is 'Hajimemashite' — it means 'Nice to meet you.'
🇯🇵 The current government is a constitutional monarchy led by Prime Minister Fumio Kishida.
🍣 For food, locals love ramen alleys in Shinjuku and okonomiyaki in Osaka.
🎵 Here's what's trending on Spotify Japan: Fujii Kaze's 'Workin' Hard'.
🗣️ Slang tip: saying 'Yabai!' means 'That's crazy!' — good or bad.
Want to hear about festivals or how to behave at dinner?"
```

## Key Features Explained

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

## Development

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

## Deployment

### Production Setup

1. **Environment Configuration**
```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://...
export REDIS_URL=redis://...
```

## Acknowledgments

- **Anthropic** - Claude AI for cultural reasoning
- **Deepgram** - Multilingual speech recognition
- **Vapi** - Voice interface platform
- **Spotify** - Music data API
- **NewsAPI** - News aggregation
- **Reddit** - Cultural insights
- **Wikipedia** - Historical data
- **Arize** - AI observability platform

## Contributors

- danchizik@berkeley.edu
- tarunshah@berkeley.edu
- vibhornarang@berkeley.edu
- Cal Hacks for hosting!!

---
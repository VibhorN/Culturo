"""
External API Integrations for WorldWise
"""

from .anthropic import AnthropicIntegration
from .deepgram import DeepgramIntegration
from .vapi import VapiIntegration
from .spotify import SpotifyIntegration
from .news import NewsAPIIntegration
from .reddit import RedditIntegration
from .tripadvisor import TripAdvisorIntegration

# Try to import Letta trivia agent
try:
    from .letta_trivia import cultural_trivia_agent
    LETTA_TRIVIA_AVAILABLE = True
except ImportError:
    LETTA_TRIVIA_AVAILABLE = False
    cultural_trivia_agent = None

__all__ = [
    'AnthropicIntegration',
    'DeepgramIntegration', 
    'VapiIntegration',
    'SpotifyIntegration',
    'NewsAPIIntegration',
    'RedditIntegration',
    'TripAdvisorIntegration'
]

if LETTA_TRIVIA_AVAILABLE:
    __all__.append('cultural_trivia_agent')

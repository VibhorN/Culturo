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

__all__ = [
    'AnthropicIntegration',
    'DeepgramIntegration', 
    'VapiIntegration',
    'SpotifyIntegration',
    'NewsAPIIntegration',
    'RedditIntegration',
    'TripAdvisorIntegration'
]

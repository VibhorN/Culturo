"""
Agent System for WorldWise
Import all agents from the agents module
"""

# Export individual agents for easy importing
from .orchestrator import OrchestratorAgent
from .language import LanguageCorrectionAgent
from .cultural import CulturalContextAgent
from .translation import TranslationAgent
from .conversation import ConversationAgent
from .evaluation import EvaluationAgent
from .personalization import PersonalizationAgent
from .data_retrieval import DataRetrievalAgent

# New agents
from .learning.pronunciation_coach import PronunciationCoachAgent
from .learning.vocabulary_builder import VocabularyBuilderAgent
from .cultural_agents.cultural_etiquette import CulturalEtiquetteAgent
from .analysis.progress_analytics import ProgressAnalyticsAgent
from .cognitive.motivation_coach import MotivationCoachAgent
from .content_feed import ContentFeedAgent
from .trivia import TriviaAgent

__all__ = [
    'OrchestratorAgent',
    'LanguageCorrectionAgent', 
    'CulturalContextAgent',
    'TranslationAgent',
    'ConversationAgent',
    'EvaluationAgent',
    'PersonalizationAgent',
    'DataRetrievalAgent',
    'PronunciationCoachAgent',
    'VocabularyBuilderAgent',
    'CulturalEtiquetteAgent',
    'ProgressAnalyticsAgent',
    'MotivationCoachAgent',
    'ContentFeedAgent',
    'TriviaAgent'
]

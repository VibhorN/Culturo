#!/usr/bin/env python3
"""
Real Agent Test Query - Simulates a user interaction that calls multiple agents
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from integrations.arize import arize_integration

def simulate_real_user_interaction():
    """Simulate a real user interaction that would call multiple agents"""
    
    print("🎯 Simulating Real User Interaction with Multiple Agents")
    print("=" * 60)
    
    # Simulate a user asking a complex question that would trigger multiple agents
    user_query = "I'm planning a trip to Paris and want to learn some French. Can you help me with basic greetings and cultural etiquette?"
    
    print(f"👤 User Query: {user_query}")
    print("\n🤖 This query would trigger multiple agents:")
    
    # Agent 1: ConversationAgent - Initial response
    print("\n1️⃣ ConversationAgent - Initial Response")
    arize_integration.log_comprehensive_agent_evaluation(
        agent_name='ConversationAgent',
        user_id='real_user_001',
        session_id='paris_trip_session_001',
        input_data={
            'user_question': user_query,
            'context': 'travel_planning',
            'language': 'english'
        },
        output_data={
            'response': 'I\'d be happy to help you prepare for your Paris trip! Let me connect you with our language learning agents to teach you French greetings and cultural etiquette.',
            'confidence': 0.92,
            'reasoning': 'Recognized travel planning request and routed to appropriate learning agents',
            'language_detected': 'english',
            'next_actions': ['VocabularyBuilder', 'CulturalEtiquette']
        },
        execution_time=1.5,
        confidence=0.92,
        status='success'
    )
    
    # Agent 2: VocabularyBuilder - French greetings
    print("2️⃣ VocabularyBuilder - French Greetings")
    arize_integration.log_comprehensive_agent_evaluation(
        agent_name='VocabularyBuilder',
        user_id='real_user_001',
        session_id='paris_trip_session_001',
        input_data={
            'word': 'bonjour',
            'context': 'greeting',
            'difficulty': 'beginner',
            'user_level': 'beginner'
        },
        output_data={
            'response': 'Bonjour means "hello" in French. It\'s pronounced "bon-ZHOOR" and is used for formal greetings throughout the day.',
            'confidence': 0.95,
            'reasoning': 'Provided accurate translation, pronunciation, and usage context for beginner',
            'pronunciation': 'bon-ZHOOR',
            'usage_examples': ['Bonjour, comment allez-vous?', 'Bonjour, madame'],
            'related_words': ['bonsoir', 'salut', 'au revoir']
        },
        execution_time=1.3,
        confidence=0.95,
        status='success'
    )
    
    # Agent 3: PronunciationCoach - Pronunciation help
    print("3️⃣ PronunciationCoach - Pronunciation Help")
    arize_integration.log_comprehensive_agent_evaluation(
        agent_name='PronunciationCoach',
        user_id='real_user_001',
        session_id='paris_trip_session_001',
        input_data={
            'word': 'bonjour',
            'language': 'french',
            'difficulty': 'beginner',
            'user_level': 'beginner'
        },
        output_data={
            'response': 'Let me help you with the pronunciation of "bonjour". The "r" is guttural - try saying "bon-ZHOOR" with a slight throat sound.',
            'confidence': 0.88,
            'reasoning': 'Provided detailed pronunciation guidance with phonetic breakdown',
            'phonetic': 'bon-ZHOOR',
            'pronunciation_tips': ['Practice the guttural r', 'Stress the second syllable'],
            'audio_available': True
        },
        execution_time=2.2,
        confidence=0.88,
        status='success'
    )
    
    # Agent 4: CulturalEtiquette - French cultural advice
    print("4️⃣ CulturalEtiquette - French Cultural Advice")
    arize_integration.log_comprehensive_agent_evaluation(
        agent_name='CulturalEtiquette',
        user_id='real_user_001',
        session_id='paris_trip_session_001',
        input_data={
            'situation': 'greeting_stranger',
            'country': 'france',
            'context': 'travel',
            'user_level': 'beginner'
        },
        output_data={
            'response': 'In France, when greeting someone, say "Bonjour" with a slight nod. In Paris, people appreciate when tourists make an effort to speak French, even if it\'s just basic greetings.',
            'confidence': 0.90,
            'reasoning': 'Provided culturally accurate advice for French greetings in travel context',
            'cultural_tips': ['Use bonjour with a slight nod', 'French people appreciate effort', 'Be polite and respectful'],
            'do_dont': ['Do: Say bonjour first', 'Don\'t: Assume everyone speaks English']
        },
        execution_time=2.0,
        confidence=0.90,
        status='success'
    )
    
    # Agent 5: EvaluationAgent - Learning progress assessment
    print("5️⃣ EvaluationAgent - Learning Progress Assessment")
    arize_integration.log_comprehensive_agent_evaluation(
        agent_name='EvaluationAgent',
        user_id='real_user_001',
        session_id='paris_trip_session_001',
        input_data={
            'interaction_data': {'words_learned': 1, 'cultural_tips_received': 3, 'pronunciation_practiced': 1},
            'user_profile': {'level': 'beginner', 'goal': 'travel_preparation'},
            'session_context': {'duration': 300, 'agents_used': 4}
        },
        output_data={
            'response': 'Excellent progress! You\'ve learned basic French greetings and cultural etiquette. Your pronunciation practice shows good engagement. Ready for your Paris trip!',
            'confidence': 0.87,
            'reasoning': 'Analyzed learning progress across multiple agents and provided encouraging feedback',
            'learning_progress': 'excellent',
            'recommendations': ['Practice bonjour pronunciation', 'Learn basic phrases like merci and excusez-moi'],
            'next_steps': ['Try ordering food in French', 'Practice numbers for shopping']
        },
        execution_time=2.8,
        confidence=0.87,
        status='success'
    )
    
    # Agent 6: MotivationCoach - Encouragement
    print("6️⃣ MotivationCoach - Encouragement")
    arize_integration.log_comprehensive_agent_evaluation(
        agent_name='MotivationCoach',
        user_id='real_user_001',
        session_id='paris_trip_session_001',
        input_data={
            'user_mood': 'excited',
            'progress_level': 'beginner',
            'achievement': 'learned_basic_greetings',
            'context': 'travel_preparation'
        },
        output_data={
            'response': 'You\'re doing fantastic! Learning French for your Paris trip shows great initiative. The French will appreciate your effort, and you\'ll have a much richer experience!',
            'confidence': 0.89,
            'reasoning': 'Provided encouraging feedback based on user achievement and travel context',
            'motivation_level': 'high',
            'encouragement': 'You\'re doing fantastic!',
            'travel_tips': ['French people appreciate effort', 'You\'ll have a richer experience']
        },
        execution_time=1.7,
        confidence=0.89,
        status='success'
    )
    
    print("\n" + "=" * 60)
    print("🎉 Real User Interaction Simulation Complete!")
    print("\n📊 This interaction triggered 6 agents:")
    print("   1️⃣ ConversationAgent - Initial response and routing")
    print("   2️⃣ VocabularyBuilder - French greetings")
    print("   3️⃣ PronunciationCoach - Pronunciation help")
    print("   4️⃣ CulturalEtiquette - French cultural advice")
    print("   5️⃣ EvaluationAgent - Learning progress assessment")
    print("   6️⃣ MotivationCoach - Encouragement")
    
    print("\n🎯 What You'll See in Arize:")
    print("   📈 6 comprehensive evaluation models")
    print("   📊 Detailed scores and reasoning for each agent")
    print("   🔍 Input/output data for each interaction")
    print("   📈 Performance metrics and quality assessment")
    
    print("\n🚀 Next Steps:")
    print("   1. Go to your Arize dashboard")
    print("   2. Navigate to 'Models' section")
    print("   3. Look for the comprehensive evaluation models")
    print("   4. Click on any model to see detailed scores and reasoning")
    print("   5. Compare different agents' performance")

if __name__ == "__main__":
    simulate_real_user_interaction()

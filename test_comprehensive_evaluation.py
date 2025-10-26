#!/usr/bin/env python3
"""
Comprehensive Agent Evaluation Test Script
Tests the comprehensive evaluation system with detailed scores and reasoning
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from integrations.arize import arize_integration

def test_comprehensive_evaluation():
    """Test comprehensive agent evaluation with detailed scores and reasoning"""
    
    print("🎯 Testing Comprehensive Agent Evaluation System")
    print("=" * 60)
    
    # Test scenarios for different agents
    test_scenarios = [
        {
            "agent_name": "ConversationAgent",
            "scenario": "Weather Inquiry",
            "input_data": {
                "user_question": "What is the weather like in Paris?",
                "context": "travel_inquiry",
                "language": "english"
            },
            "output_data": {
                "response": "The weather in Paris is currently sunny with 22°C. Perfect for sightseeing! I recommend visiting the Eiffel Tower and taking a Seine river cruise.",
                "confidence": 0.9,
                "reasoning": "Used weather API and provided helpful travel advice with specific recommendations",
                "language_detected": "english",
                "suggestions": ["Eiffel Tower", "Seine river cruise"]
            },
            "execution_time": 1.8,
            "confidence": 0.9,
            "status": "success"
        },
        {
            "agent_name": "VocabularyBuilder",
            "scenario": "French Greeting",
            "input_data": {
                "word": "bonjour",
                "context": "greeting",
                "difficulty": "beginner"
            },
            "output_data": {
                "response": "Bonjour means hello in French. It is pronounced \"bon-ZHOOR\" and is used for formal greetings.",
                "confidence": 0.95,
                "reasoning": "Provided accurate translation, pronunciation guide, and usage context",
                "pronunciation": "bon-ZHOOR",
                "usage_examples": ["Bonjour, comment allez-vous?"]
            },
            "execution_time": 1.2,
            "confidence": 0.95,
            "status": "success"
        },
        {
            "agent_name": "EvaluationAgent",
            "scenario": "Learning Progress Assessment",
            "input_data": {
                "interaction_data": {"questions_answered": 5, "accuracy": 0.85},
                "user_profile": {"level": "intermediate"},
                "session_context": {"duration": 300}
            },
            "output_data": {
                "response": "Your learning progress is excellent! You answered 5 questions with 85% accuracy, showing strong improvement.",
                "confidence": 0.88,
                "reasoning": "Analyzed user performance metrics and provided encouraging feedback with specific achievements",
                "learning_progress": "excellent",
                "recommendations": ["Continue practicing vocabulary", "Try more advanced exercises"]
            },
            "execution_time": 2.5,
            "confidence": 0.88,
            "status": "success"
        },
        {
            "agent_name": "PronunciationCoach",
            "scenario": "Pronunciation Practice",
            "input_data": {
                "word": "croissant",
                "language": "french",
                "difficulty": "intermediate"
            },
            "output_data": {
                "response": "Croissant is pronounced \"kwah-SAHN\" in French. The 'r' is guttural and the 't' is silent.",
                "confidence": 0.92,
                "reasoning": "Provided accurate pronunciation with phonetic breakdown and specific guidance",
                "phonetic": "kwah-SAHN",
                "tips": ["Practice the guttural 'r'", "Remember the silent 't'"]
            },
            "execution_time": 2.1,
            "confidence": 0.92,
            "status": "success"
        },
        {
            "agent_name": "CulturalEtiquette",
            "scenario": "Cultural Advice",
            "input_data": {
                "situation": "business_meeting",
                "country": "japan",
                "context": "professional"
            },
            "output_data": {
                "response": "In Japanese business meetings, bow slightly when greeting, exchange business cards with both hands, and avoid direct eye contact.",
                "confidence": 0.87,
                "reasoning": "Provided culturally accurate advice based on Japanese business etiquette",
                "cultural_tips": ["Bow slightly", "Exchange cards with both hands", "Avoid direct eye contact"],
                "importance": "high"
            },
            "execution_time": 2.3,
            "confidence": 0.87,
            "status": "success"
        },
        {
            "agent_name": "MotivationCoach",
            "scenario": "Learning Motivation",
            "input_data": {
                "user_mood": "frustrated",
                "progress_level": "beginner",
                "challenge": "difficult_grammar"
            },
            "output_data": {
                "response": "Don't worry! Grammar challenges are normal for beginners. You're making great progress! Try breaking it into smaller pieces.",
                "confidence": 0.85,
                "reasoning": "Provided encouraging and supportive feedback with practical advice",
                "motivation_level": "high",
                "encouragement": "You're making great progress!"
            },
            "execution_time": 1.6,
            "confidence": 0.85,
            "status": "success"
        }
    ]
    
    # Test each scenario
    for i, scenario in enumerate(test_scenarios):
        print(f"\n📊 Testing {scenario['agent_name']} - {scenario['scenario']}")
        
        try:
            arize_integration.log_comprehensive_agent_evaluation(
                agent_name=scenario['agent_name'],
                user_id=f'comprehensive_test_user_{i+1:03d}',
                session_id=f'comprehensive_test_session_{i+1:03d}',
                input_data=scenario['input_data'],
                output_data=scenario['output_data'],
                execution_time=scenario['execution_time'],
                confidence=scenario['confidence'],
                status=scenario['status']
            )
            
            print(f"✅ {scenario['agent_name']} comprehensive evaluation logged")
            
        except Exception as e:
            print(f"❌ Failed to log {scenario['agent_name']}: {str(e)}")
        
        # Small delay between tests
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive Evaluation System Test Complete!")
    print("\n📊 What You'll See in Arize Models:")
    print("   - ConversationAgent_comprehensive_evaluation")
    print("   - VocabularyBuilder_comprehensive_evaluation")
    print("   - EvaluationAgent_comprehensive_evaluation")
    print("   - PronunciationCoach_comprehensive_evaluation")
    print("   - CulturalEtiquette_comprehensive_evaluation")
    print("   - MotivationCoach_comprehensive_evaluation")
    
    print("\n🔍 Each Model Contains:")
    print("   📈 Overall Score (0.0-1.0)")
    print("   📈 Response Quality Score + Detailed Reasoning")
    print("   📈 Performance Score + Detailed Reasoning")
    print("   📈 Accuracy Score + Detailed Reasoning")
    print("   📈 Relevance Score + Detailed Reasoning")
    print("   📈 User Experience Score + Detailed Reasoning")
    print("   📊 Flattened Input/Output Data")
    print("   🏷️  Agent-specific Tags")
    
    print("\n🎯 Next Steps:")
    print("   1. Go to your Arize dashboard")
    print("   2. Navigate to 'Models' section")
    print("   3. Look for the comprehensive evaluation models")
    print("   4. Click on any model to see detailed scores and reasoning")
    print("   5. Explore the features to see input/output data")
    
    print("\n💡 This gives you comprehensive agent evaluation with:")
    print("   ✅ Detailed scores for each agent")
    print("   ✅ Reasoning for every score")
    print("   ✅ Performance tracking")
    print("   ✅ Quality assessment")
    print("   ✅ User experience metrics")

if __name__ == "__main__":
    test_comprehensive_evaluation()

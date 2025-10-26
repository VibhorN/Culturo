#!/usr/bin/env python3
"""
Consolidated Chat Evaluation System
Simulates a chat session that uses multiple agents and logs one consolidated evaluation row
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from integrations.arize import arize_integration

def simulate_chat_with_consolidated_evaluation():
    """Simulate a chat session that uses multiple agents and logs one consolidated evaluation"""
    
    print("🎯 Simulating Chat Session with Consolidated Evaluation")
    print("=" * 60)
    
    # Chat session details
    chat_session_id = f"consolidated_chat_{int(time.time())}"
    user_id = "consolidated_user_001"
    chat_input = "I'm planning a trip to Paris and want to learn some French. Can you help me with basic greetings and cultural etiquette?"
    
    print(f"👤 User Query: {chat_input}")
    print(f"🆔 Chat Session ID: {chat_session_id}")
    print(f"👤 User ID: {user_id}")
    
    # Simulate agents being called during the chat
    agent_evaluations = {}
    
    # Agent 1: ConversationAgent
    print("\n1️⃣ Evaluating ConversationAgent...")
    conv_eval = arize_integration._calculate_comprehensive_scores(
        "ConversationAgent",
        {"user_question": chat_input, "context": "travel_planning"},
        {"response": "I'd be happy to help you prepare for your Paris trip! Let me connect you with our language learning agents.", "confidence": 0.92},
        1.5,
        0.92,
        "success"
    )
    conv_reasoning = arize_integration._generate_evaluation_reasoning(
        "ConversationAgent",
        {"user_question": chat_input},
        {"response": "I'd be happy to help you prepare for your Paris trip!"},
        conv_eval,
        "success"
    )
    agent_evaluations["ConversationAgent"] = {
        **conv_eval,
        **conv_reasoning,
        "execution_time": 1.5,
        "confidence": 0.92,
        "status": "success"
    }
    
    # Agent 2: VocabularyBuilder
    print("2️⃣ Evaluating VocabularyBuilder...")
    vocab_eval = arize_integration._calculate_comprehensive_scores(
        "VocabularyBuilder",
        {"word": "bonjour", "context": "greeting", "difficulty": "beginner"},
        {"response": "Bonjour means hello in French. It's pronounced 'bon-ZHOOR' and is used for formal greetings.", "confidence": 0.95},
        1.2,
        0.95,
        "success"
    )
    vocab_reasoning = arize_integration._generate_evaluation_reasoning(
        "VocabularyBuilder",
        {"word": "bonjour"},
        {"response": "Bonjour means hello in French."},
        vocab_eval,
        "success"
    )
    agent_evaluations["VocabularyBuilder"] = {
        **vocab_eval,
        **vocab_reasoning,
        "execution_time": 1.2,
        "confidence": 0.95,
        "status": "success"
    }
    
    # Agent 3: PronunciationCoach
    print("3️⃣ Evaluating PronunciationCoach...")
    pron_eval = arize_integration._calculate_comprehensive_scores(
        "PronunciationCoach",
        {"word": "bonjour", "language": "french", "difficulty": "beginner"},
        {"response": "Let me help you with the pronunciation of 'bonjour'. The 'r' is guttural - try saying 'bon-ZHOOR'.", "confidence": 0.88},
        2.1,
        0.88,
        "success"
    )
    pron_reasoning = arize_integration._generate_evaluation_reasoning(
        "PronunciationCoach",
        {"word": "bonjour"},
        {"response": "Let me help you with the pronunciation of 'bonjour'."},
        pron_eval,
        "success"
    )
    agent_evaluations["PronunciationCoach"] = {
        **pron_eval,
        **pron_reasoning,
        "execution_time": 2.1,
        "confidence": 0.88,
        "status": "success"
    }
    
    # Agent 4: CulturalEtiquette
    print("4️⃣ Evaluating CulturalEtiquette...")
    cult_eval = arize_integration._calculate_comprehensive_scores(
        "CulturalEtiquette",
        {"situation": "greeting_stranger", "country": "france", "context": "travel"},
        {"response": "In France, when greeting someone, say 'Bonjour' with a slight nod. French people appreciate when tourists make an effort to speak French.", "confidence": 0.90},
        2.0,
        0.90,
        "success"
    )
    cult_reasoning = arize_integration._generate_evaluation_reasoning(
        "CulturalEtiquette",
        {"situation": "greeting_stranger"},
        {"response": "In France, when greeting someone, say 'Bonjour' with a slight nod."},
        cult_eval,
        "success"
    )
    agent_evaluations["CulturalEtiquette"] = {
        **cult_eval,
        **cult_reasoning,
        "execution_time": 2.0,
        "confidence": 0.90,
        "status": "success"
    }
    
    # Agent 5: EvaluationAgent
    print("5️⃣ Evaluating EvaluationAgent...")
    eval_eval = arize_integration._calculate_comprehensive_scores(
        "EvaluationAgent",
        {"interaction_data": {"words_learned": 1, "cultural_tips_received": 2}, "user_profile": {"level": "beginner"}},
        {"response": "Excellent progress! You've learned basic French greetings and cultural etiquette. Ready for your Paris trip!", "confidence": 0.87},
        2.5,
        0.87,
        "success"
    )
    eval_reasoning = arize_integration._generate_evaluation_reasoning(
        "EvaluationAgent",
        {"interaction_data": {"words_learned": 1}},
        {"response": "Excellent progress! You've learned basic French greetings."},
        eval_eval,
        "success"
    )
    agent_evaluations["EvaluationAgent"] = {
        **eval_eval,
        **eval_reasoning,
        "execution_time": 2.5,
        "confidence": 0.87,
        "status": "success"
    }
    
    # Calculate overall chat score
    overall_chat_score = sum(eval["overall_score"] for eval in agent_evaluations.values()) / len(agent_evaluations)
    
    # Create chat summary
    chat_summary = f"User asked about Paris trip preparation. {len(agent_evaluations)} agents provided comprehensive language learning and cultural guidance."
    
    print(f"\n📊 Chat Evaluation Summary:")
    print(f"   Overall Chat Score: {overall_chat_score:.2f}")
    print(f"   Agents Used: {len(agent_evaluations)}")
    print(f"   Chat Summary: {chat_summary}")
    
    # Log consolidated evaluation
    print(f"\n📝 Logging consolidated chat evaluation...")
    arize_integration.log_consolidated_chat_evaluation(
        chat_session_id=chat_session_id,
        user_id=user_id,
        chat_input=chat_input,
        agent_evaluations=agent_evaluations,
        overall_chat_score=overall_chat_score,
        chat_summary=chat_summary
    )
    
    print(f"\n" + "=" * 60)
    print("🎉 Consolidated Chat Evaluation Complete!")
    print(f"\n📊 What You'll See in Arize:")
    print(f"   Model: consolidated_chat_evaluations")
    print(f"   One row for this chat session: {chat_session_id}")
    print(f"\n🔍 Columns in the row:")
    print(f"   📈 overall_chat_score: {overall_chat_score:.2f}")
    print(f"   📝 chat_input: {chat_input[:50]}...")
    print(f"   📊 chat_summary: {chat_summary}")
    print(f"   👥 agents_used: {list(agent_evaluations.keys())}")
    print(f"   📊 total_agents_used: {len(agent_evaluations)}")
    
    for agent_name in agent_evaluations.keys():
        score = agent_evaluations[agent_name]["overall_score"]
        reason = agent_evaluations[agent_name]["overall_reason"]
        print(f"\n   🤖 {agent_name}:")
        print(f"      📈 {agent_name}_score: {score:.2f}")
        print(f"      💭 {agent_name}_reason: {reason}")
        print(f"      ⚡ {agent_name}_performance: {agent_evaluations[agent_name]['performance_score']:.2f}")
        print(f"      🎯 {agent_name}_accuracy: {agent_evaluations[agent_name]['accuracy_score']:.2f}")
        print(f"      🔗 {agent_name}_relevance: {agent_evaluations[agent_name]['relevance_score']:.2f}")
        print(f"      😊 {agent_name}_user_experience: {agent_evaluations[agent_name]['user_experience_score']:.2f}")
    
    print(f"\n🎯 This gives you exactly what you wanted:")
    print(f"   ✅ One row per chat session")
    print(f"   ✅ Columns for each agent's score")
    print(f"   ✅ Columns for evaluation reasons")
    print(f"   ✅ Comprehensive evaluation of all agents used")

if __name__ == "__main__":
    simulate_chat_with_consolidated_evaluation()

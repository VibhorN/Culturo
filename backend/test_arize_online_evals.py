#!/usr/bin/env python3
"""
Test script for Arize Online Evals with proper columns
"""

import os
import asyncio
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_arize_online_evals():
    """Test the Arize Online Evals integration with proper columns"""
    
    print("🔍 Testing Arize Online Evals with Proper Columns...")
    print("=" * 60)
    
    # Check environment variables
    print("1. Checking Environment Variables:")
    arize_space_id = os.getenv('ARIZE_SPACE_ID')
    arize_api_key = os.getenv('ARIZE_API_KEY')
    arize_project = os.getenv('ARIZE_PROJECT_NAME', 'lingua-cal-agents')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"   ARIZE_SPACE_ID: {arize_space_id[:20] + '...' if arize_space_id else '❌ NOT SET'}")
    print(f"   ARIZE_API_KEY: {arize_api_key[:20] + '...' if arize_api_key else '❌ NOT SET'}")
    print(f"   ARIZE_PROJECT_NAME: {arize_project}")
    print(f"   ANTHROPIC_API_KEY: {anthropic_key[:20] + '...' if anthropic_key else '❌ NOT SET'}")
    
    if not arize_space_id or not arize_api_key:
        print("\n❌ Missing Arize credentials! Please check your .env file.")
        return
    
    # Test Arize Online Evals
    print("\n2. Testing Arize Online Evals Integration:")
    try:
        from integrations.arize_online_evals import arize_online_evals, log_query_evaluation
        
        if arize_online_evals.enabled:
            print("   ✅ Arize Online Evals integration is enabled")
        else:
            print("   ❌ Arize Online Evals integration is disabled")
            return
            
    except Exception as e:
        print(f"   ❌ Error importing Arize Online Evals: {e}")
        return
    
    # Initialize Anthropic client
    print("\n3. Initializing Anthropic Client:")
    anthropic_client = None
    if anthropic_key:
        try:
            import anthropic
            anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
            print("   ✅ Anthropic client initialized")
        except Exception as e:
            print(f"   ⚠️  Anthropic client failed: {e}")
    else:
        print("   ⚠️  ANTHROPIC_API_KEY not set")
    
    # Test Online Evals
    print("\n4. Testing Query Evaluation with Proper Columns:")
    try:
        # Mock agent data
        agents_used = {
            "conversation": {
                "output_data": {"response": "Test response about Italian culture", "confidence": 0.9},
                "execution_time": 1.5,
                "confidence": 0.9,
                "status": "success",
                "usage_reason": "Processed user query about Italian culture"
            },
            "cultural_etiquette": {
                "output_data": {"etiquette_tips": ["Greet with handshake", "Dress formally"], "confidence": 0.8},
                "execution_time": 2.0,
                "confidence": 0.8,
                "status": "success", 
                "usage_reason": "Provided cultural etiquette guidance"
            },
            "data_retrieval": {
                "output_data": {"data_count": 5, "sources": ["wikipedia", "travel_guide"]},
                "execution_time": 1.2,
                "confidence": 0.7,
                "status": "success",
                "usage_reason": "Retrieved cultural data from multiple sources"
            }
        }
        
        # Test Online Evals
        log_query_evaluation(
            user_id="test_user_online_evals",
            question="What are the cultural etiquette rules in Italy?",
            response="In Italy, it's important to greet with a firm handshake, dress formally for business meetings, and avoid discussing politics or religion at dinner.",
            agents_used=agents_used,
            anthropic_client=anthropic_client
        )
        
        print("   ✅ Query evaluation logged successfully!")
        print("   📊 Check your Arize dashboard for the new data")
        print("   🔍 Look for model: agent_evaluations")
        print("   📋 You should see separate columns for each agent:")
        print("      - conversation_score, conversation_score_explanation")
        print("      - cultural_etiquette_score, cultural_etiquette_score_explanation")
        print("      - data_retrieval_score, data_retrieval_score_explanation")
        print("      - Plus relevance, quality, helpfulness scores for each agent")
        
    except Exception as e:
        print(f"   ❌ Error logging evaluation: {e}")
        import traceback
        print(f"   Full traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_arize_online_evals())

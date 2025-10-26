#!/usr/bin/env python3
"""
Simple Arize Direct Test
Tests direct Arize logging without backend processing
"""

import os
import asyncio
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def simple_arize_test():
    """Test direct Arize logging"""
    
    print("🔍 Simple Arize Direct Test")
    print("=" * 40)
    
    # Check environment variables
    print("1. Environment Variables:")
    arize_space_id = os.getenv('ARIZE_SPACE_ID')
    arize_api_key = os.getenv('ARIZE_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"   ARIZE_SPACE_ID: {arize_space_id[:20] + '...' if arize_space_id else '❌ NOT SET'}")
    print(f"   ARIZE_API_KEY: {arize_api_key[:20] + '...' if arize_api_key else '❌ NOT SET'}")
    print(f"   ANTHROPIC_API_KEY: {anthropic_key[:20] + '...' if anthropic_key else '❌ NOT SET'}")
    
    # Test direct Arize logging
    print("\n2. Testing Direct Arize Logging:")
    try:
        from integrations.arize_agent_evaluations import log_query_evaluation
        
        # Initialize Anthropic client
        anthropic_client = None
        if anthropic_key:
            import anthropic
            anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
            print("   ✅ Anthropic client initialized")
        
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
        
        # Log directly to Arize
        print("   📤 Logging to Arize...")
        log_query_evaluation(
            user_id="test_user_direct",
            question="What are the cultural etiquette rules in Italy?",
            response="In Italy, it's important to greet with a firm handshake, dress formally for business meetings, and avoid discussing politics or religion at dinner.",
            agents_used=agents_used,
            anthropic_client=anthropic_client
        )
        
        print("   ✅ Direct Arize logging successful!")
        print("\n📊 Check your Arize dashboard:")
        print("   1. Go to 'Datasets & Experiments'")
        print("   2. Look for 'agent-evaluations' project")
        print("   3. You should see columns for each agent:")
        print("      - conversation_score, conversation_score_explanation")
        print("      - cultural_etiquette_score, cultural_etiquette_score_explanation")
        print("      - data_retrieval_score, data_retrieval_score_explanation")
        print("      - Plus relevance, quality, helpfulness scores")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        print(f"   Full traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(simple_arize_test())

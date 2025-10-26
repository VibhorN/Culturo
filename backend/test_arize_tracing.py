#!/usr/bin/env python3
"""
Test script for Arize OpenTelemetry Tracing
"""

import os
import asyncio
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_arize_tracing():
    """Test the Arize tracing integration"""
    
    print("🔍 Testing Arize OpenTelemetry Tracing...")
    print("=" * 50)
    
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
    
    # Test Arize tracing
    print("\n2. Testing Arize Tracing Integration:")
    try:
        from integrations.arize_tracing import arize_tracing, log_query_evaluation
        
        if arize_tracing.enabled:
            print("   ✅ Arize tracing integration is enabled")
        else:
            print("   ❌ Arize tracing integration is disabled")
            return
            
    except Exception as e:
        print(f"   ❌ Error importing Arize tracing: {e}")
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
    
    # Test tracing
    print("\n4. Testing Query Tracing:")
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
        
        # Test tracing
        log_query_evaluation(
            user_id="test_user_tracing",
            question="What are the cultural etiquette rules in Italy?",
            response="In Italy, it's important to greet with a firm handshake, dress formally for business meetings, and avoid discussing politics or religion at dinner.",
            agents_used=agents_used,
            anthropic_client=anthropic_client
        )
        
        print("   ✅ Query trace logged successfully!")
        print("   📊 Check your Arize LLM Tracing dashboard for the new trace")
        print("   🔍 Look for traces with user_id: test_user_tracing")
        
    except Exception as e:
        print(f"   ❌ Error logging trace: {e}")
        import traceback
        print(f"   Full traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_arize_tracing())

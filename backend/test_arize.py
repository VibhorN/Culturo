#!/usr/bin/env python3
"""
Test script to diagnose Arize integration issues
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_arize_integration():
    """Test the simplified Arize integration"""
    
    print("🔍 Diagnosing Arize Integration...")
    print("=" * 50)
    
    # Check environment variables
    print("1. Checking Environment Variables:")
    arize_space_id = os.getenv('ARIZE_SPACE_ID')
    arize_api_key = os.getenv('ARIZE_API_KEY')
    arize_project = os.getenv('ARIZE_PROJECT_NAME', 'lingua-cal-agents')
    
    print(f"   ARIZE_SPACE_ID: {arize_space_id[:20] + '...' if arize_space_id else '❌ NOT SET'}")
    print(f"   ARIZE_API_KEY: {arize_api_key[:20] + '...' if arize_api_key else '❌ NOT SET'}")
    print(f"   ARIZE_PROJECT_NAME: {arize_project}")
    
    if not arize_space_id or not arize_api_key:
        print("\n❌ Missing Arize credentials! Please check your .env file.")
        return
    
    # Test Arize client connection
    print("\n2. Testing Arize Client Connection:")
    try:
        from integrations.simplified_arize import simplified_arize
        print(f"   Simplified Arize enabled: {simplified_arize.enabled}")
        
        if simplified_arize.enabled:
            print("   ✅ Simplified Arize integration is enabled")
        else:
            print("   ❌ Simplified Arize integration is disabled")
            return
            
    except Exception as e:
        print(f"   ❌ Error importing simplified Arize: {e}")
        return
    
    # Test actual logging
    print("\n3. Testing Query Logging:")
    try:
        # Mock agent data
        agents_used = {
            "conversation": {
                "output_data": {"response": "Test response", "confidence": 0.9},
                "execution_time": 1.5,
                "confidence": 0.9,
                "status": "success",
                "usage_reason": "Test query"
            },
            "data_retrieval": {
                "output_data": {"status": "success", "data_count": 5},
                "execution_time": 2.0,
                "confidence": 0.8,
                "status": "success", 
                "usage_reason": "Test query"
            }
        }
        
        # Initialize Anthropic client
        anthropic_client = None
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            try:
                import anthropic
                anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                print("   ✅ Anthropic client initialized")
            except Exception as e:
                print(f"   ⚠️  Anthropic client failed: {e}")
        else:
            print("   ⚠️  ANTHROPIC_API_KEY not set")
        
        # Test logging
        await simplified_arize.log_query_with_agent_evaluations(
            user_id="test_user",
            question="Test question about Italian food",
            response="Test response about Italian cuisine",
            agents_used=agents_used,
            anthropic_client=anthropic_client
        )
        
        print("   ✅ Query logged successfully!")
        print("   📊 Check your Arize dashboard for the new log entry")
        
    except Exception as e:
        print(f"   ❌ Error logging query: {e}")
        print(f"   Error details: {type(e).__name__}: {str(e)}")
        
        # Try to get more details
        import traceback
        print(f"   Full traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_arize_integration())

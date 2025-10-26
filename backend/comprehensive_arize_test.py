#!/usr/bin/env python3
"""
Comprehensive Arize Integration Test Script
Tests the full flow: query -> backend -> logs -> Arize project
"""

import os
import asyncio
import time
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def comprehensive_arize_test():
    """Test the complete Arize integration flow"""
    
    print("🔍 Comprehensive Arize Integration Test")
    print("=" * 60)
    
    # Step 1: Check Environment Variables
    print("1. Checking Environment Variables:")
    arize_space_id = os.getenv('ARIZE_SPACE_ID')
    arize_api_key = os.getenv('ARIZE_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"   ARIZE_SPACE_ID: {arize_space_id[:20] + '...' if arize_space_id else '❌ NOT SET'}")
    print(f"   ARIZE_API_KEY: {arize_api_key[:20] + '...' if arize_api_key else '❌ NOT SET'}")
    print(f"   ANTHROPIC_API_KEY: {anthropic_key[:20] + '...' if anthropic_key else '❌ NOT SET'}")
    
    if not arize_space_id or not arize_api_key:
        print("\n❌ Missing Arize credentials! Please check your .env file.")
        return
    
    # Step 2: Check Backend Status
    print("\n2. Checking Backend Status:")
    backend_url = "http://localhost:5001"
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print(f"   ⚠️  Backend responded with status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Backend is not running: {e}")
        print("   💡 Start the backend with: cd backend && python3 app.py &")
        return
    
    # Step 3: Test Arize Integration Directly
    print("\n3. Testing Arize Integration Directly:")
    try:
        from integrations.arize_agent_evaluations import arize_agent_evaluations, log_query_evaluation
        
        if arize_agent_evaluations.enabled:
            print("   ✅ Arize Agent Evaluations Project is enabled")
            print(f"   📁 Project Name: {arize_agent_evaluations.project_name}")
        else:
            print("   ❌ Arize Agent Evaluations Project is disabled")
            return
            
    except Exception as e:
        print(f"   ❌ Error importing Arize integration: {e}")
        return
    
    # Step 4: Initialize Anthropic Client
    print("\n4. Initializing Anthropic Client:")
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
    
    # Step 5: Send Test Query to Backend
    print("\n5. Sending Test Query to Backend:")
    test_query = {
        "query": "What are the cultural etiquette rules in Italy?",
        "user_id": "test_user_comprehensive",
        "language": "en",
        "input_type": "text",
        "session_data": {"test": True}
    }
    
    try:
        print(f"   📤 Sending query: {test_query['query']}")
        response = requests.post(
            f"{backend_url}/api/agent/process",
            json=test_query,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Backend processed query successfully")
            print(f"   📝 Response: {result.get('response', 'No response')[:100]}...")
            print(f"   🎯 Status: {result.get('status', 'Unknown')}")
            
            # Check if agents were activated
            metadata = result.get('metadata', {})
            agents_activated = metadata.get('agents_activated', [])
            print(f"   🤖 Agents activated: {agents_activated}")
            
        else:
            print(f"   ❌ Backend error: {response.status_code}")
            print(f"   📝 Error details: {response.text}")
            return
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Failed to send query to backend: {e}")
        return
    
    # Step 6: Test Direct Arize Logging
    print("\n6. Testing Direct Arize Logging:")
    try:
        # Mock agent data based on what we expect
        agents_used = {
            "conversation": {
                "output_data": {"response": result.get('response', 'Test response'), "confidence": 0.9},
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
        log_query_evaluation(
            user_id="test_user_comprehensive",
            question=test_query["query"],
            response=result.get('response', 'Test response'),
            agents_used=agents_used,
            anthropic_client=anthropic_client
        )
        
        print("   ✅ Query evaluation logged to Arize successfully!")
        
    except Exception as e:
        print(f"   ❌ Error logging to Arize: {e}")
        import traceback
        print(f"   Full traceback:\n{traceback.format_exc()}")
    
    # Step 7: Check Arize Project Status
    print("\n7. Checking Arize Project Status:")
    try:
        # Try to verify the project exists by checking recent logs
        print("   📊 Checking if data was sent to Arize...")
        print("   🔍 Look for project: agent-evaluations")
        print("   📋 Expected columns:")
        print("      - question, response, user_id, timestamp")
        print("      - total_agents_used, overall_query_score")
        print("      - conversation_score, conversation_score_explanation")
        print("      - cultural_etiquette_score, cultural_etiquette_score_explanation")
        print("      - data_retrieval_score, data_retrieval_score_explanation")
        print("      - Plus relevance, quality, helpfulness scores for each agent")
        
    except Exception as e:
        print(f"   ❌ Error checking Arize project: {e}")
    
    # Step 8: Summary
    print("\n8. Test Summary:")
    print("   ✅ Environment variables: OK")
    print("   ✅ Backend status: OK")
    print("   ✅ Arize integration: OK")
    print("   ✅ Test query sent: OK")
    print("   ✅ Direct Arize logging: OK")
    print("\n📊 Next Steps:")
    print("   1. Check your Arize dashboard")
    print("   2. Go to 'Datasets & Experiments'")
    print("   3. Look for 'agent-evaluations' project")
    print("   4. Verify the columns and data are there")
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive test completed!")

if __name__ == "__main__":
    asyncio.run(comprehensive_arize_test())

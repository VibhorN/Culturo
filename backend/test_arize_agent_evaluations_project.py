#!/usr/bin/env python3
"""
Test script for Arize Agent Evaluations Project
"""

import os
import asyncio
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_arize_agent_evaluations_project():
    """Test the Arize Agent Evaluations Project"""
    
    print("🔍 Testing Arize Agent Evaluations Project...")
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
    
    # Test Arize Agent Evaluations Project
    print("\n2. Testing Arize Agent Evaluations Project:")
    try:
        from integrations.arize_agent_evaluations import arize_agent_evaluations, log_query_evaluation
        
        if arize_agent_evaluations.enabled:
            print("   ✅ Arize Agent Evaluations Project is enabled")
            print(f"   📁 Project Name: {arize_agent_evaluations.project_name}")
        else:
            print("   ❌ Arize Agent Evaluations Project is disabled")
            return
            
    except Exception as e:
        print(f"   ❌ Error importing Arize Agent Evaluations Project: {e}")
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
    
    # Test Agent Evaluations Project
    print("\n4. Testing Agent Evaluations Project:")
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
        
        # Test Agent Evaluations Project
        log_query_evaluation(
            user_id="test_user_project",
            question="What are the cultural etiquette rules in Italy?",
            response="In Italy, it's important to greet with a firm handshake, dress formally for business meetings, and avoid discussing politics or religion at dinner.",
            agents_used=agents_used,
            anthropic_client=anthropic_client
        )
        
        print("   ✅ Query evaluation logged to dedicated project!")
        print("   📊 Check your Arize dashboard for the new project")
        print("   🔍 Look for project: agent-evaluations")
        print("   📋 You should see a dedicated project with these columns:")
        print("      - question, response, user_id, timestamp")
        print("      - total_agents_used, overall_query_score")
        print("      - For each agent:")
        print("        * {agent_name}_used, {agent_name}_usage_reason")
        print("        * {agent_name}_execution_time_ms, {agent_name}_confidence")
        print("        * {agent_name}_status, {agent_name}_score")
        print("        * {agent_name}_score_explanation")
        print("        * {agent_name}_relevance_score, {agent_name}_quality_score")
        print("        * {agent_name}_helpfulness_score")
        print("        * {agent_name}_strengths, {agent_name}_improvements")
        
    except Exception as e:
        print(f"   ❌ Error logging to project: {e}")
        import traceback
        print(f"   Full traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_arize_agent_evaluations_project())

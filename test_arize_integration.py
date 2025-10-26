#!/usr/bin/env python3
"""
Test script for Arize integration
Run this to verify that Arize is properly configured
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

async def test_arize_integration():
    """Test Arize integration"""
    print("🧪 Testing Arize integration...")
    
    try:
        from integrations.arize import arize_integration
        
        if not arize_integration.enabled:
            print("❌ Arize integration is disabled")
            print("   Check your environment variables:")
            print("   - ARIZE_SPACE_ID")
            print("   - ARIZE_API_KEY")
            return False
        
        print("✅ Arize integration is enabled")
        
        # Test logging a sample agent execution
        test_data = {
            "agent_name": "TestAgent",
            "user_id": "test_user_123",
            "session_id": "test_session_456",
            "input_data": {"test": "input"},
            "output_data": {"test": "output", "confidence": 0.8},
            "execution_time": 1.5,
            "confidence": 0.8,
            "status": "success"
        }
        
        arize_integration.log_agent_execution(**test_data)
        print("✅ Successfully logged test agent execution")
        
        # Test logging evaluation result
        arize_integration.log_evaluation_result(
            agent_name="TestAgent",
            user_id="test_user_123",
            evaluation_type="test_evaluation",
            evaluation_data={"score": 0.85},
            score=0.85
        )
        print("✅ Successfully logged test evaluation result")
        
        # Test logging user interaction
        arize_integration.log_user_interaction(
            user_id="test_user_123",
            interaction_type="test_interaction",
            interaction_data={"satisfaction": 0.9},
            satisfaction_score=0.9
        )
        print("✅ Successfully logged test user interaction")
        
        print("\n🎉 All tests passed! Arize integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_arize_integration())
    sys.exit(0 if success else 1)

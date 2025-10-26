#!/usr/bin/env python3
"""
Simple Test Script for WorldWise Multilingual Voice Integration
"""

import requests
import json
import os

# API Keys
VAPI_API_KEY = os.getenv('VAPI_API_KEY', 'dcedb61d-8e71-4a84-9f31-b092891666f9')
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY', '7a2884444ff84cfd012c51d735c625f28ed795f9')

# Base URL
BASE_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_vapi_assistant_creation():
    """Test creating a Vapi assistant for a specific language"""
    print("🎤 Testing Vapi assistant creation...")
    
    # Test with Spanish
    data = {"language": "es-ES"}
    
    response = requests.post(
        f"{BASE_URL}/api/hybrid/start-conversation",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_multilingual_voices():
    """Test creating assistants for different languages"""
    print("🌍 Testing multilingual voice assistants...")
    
    languages = [
        ("en-US", "English"),
        ("es-ES", "Spanish"),
        ("fr-FR", "French"),
        ("de-DE", "German"),
        ("ja-JP", "Japanese")
    ]
    
    for lang_code, lang_name in languages:
        print(f"\n🔤 Creating {lang_name} ({lang_code}) assistant...")
        
        data = {"language": lang_code}
        response = requests.post(
            f"{BASE_URL}/api/hybrid/start-conversation",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {lang_name}: {result.get('voice', 'N/A')}")
            print(f"   Assistant ID: {result.get('assistant_id', 'N/A')}")
            print(f"   Widget URL: {result.get('widget_url', 'N/A')}")
        else:
            print(f"❌ {lang_name}: Failed - {response.status_code}")
            print(f"   Error: {response.text}")

def main():
    """Main test function"""
    print("🚀 WORLDWISE MULTILINGUAL VOICE INTEGRATION TEST")
    print("=" * 60)
    print()
    
    # Test 1: Health check
    test_health()
    
    # Test 2: Single language assistant
    # test_vapi_assistant_creation()
    
    # Test 3: Multiple languages
    # test_multilingual_voices()
    
    print("✅ Tests completed!")

if __name__ == "__main__":
    main()

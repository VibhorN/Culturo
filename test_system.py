#!/usr/bin/env python3

"""
WorldWise System Test Script
Tests the core functionality of the cultural data aggregation system
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app import CulturalDataAggregator

async def test_cultural_data_aggregation():
    """Test the cultural data aggregation system"""
    print("🌍 Testing WorldWise Cultural Data Aggregation")
    print("=" * 50)
    
    # Initialize the aggregator
    aggregator = CulturalDataAggregator()
    
    # Test countries
    test_countries = ["Japan", "Korea", "Italy", "Mexico", "India"]
    
    for country in test_countries:
        print(f"\n🔍 Testing cultural data for {country}...")
        
        try:
            # Get cultural data
            start_time = datetime.now()
            cultural_data = await aggregator.get_cultural_data(country)
            end_time = datetime.now()
            
            # Calculate response time
            response_time = (end_time - start_time).total_seconds()
            
            # Display results
            print(f"✅ Success! Response time: {response_time:.2f}s")
            
            # Show data summary
            if cultural_data and not cultural_data.get('error'):
                print(f"   📊 Data sources:")
                for key, value in cultural_data.items():
                    if value and key != 'country' and key != 'language' and key != 'timestamp':
                        source = value.get('source', 'Unknown') if isinstance(value, dict) else 'Sample data'
                        print(f"      - {key.title()}: {source}")
            else:
                print(f"   ⚠️  No data or error: {cultural_data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error testing {country}: {str(e)}")
    
    print(f"\n🎉 Cultural data aggregation test completed!")

async def test_individual_components():
    """Test individual API components"""
    print("\n🔧 Testing Individual Components")
    print("=" * 40)
    
    aggregator = CulturalDataAggregator()
    
    # Test government info
    print("\n🏛️  Testing government info...")
    try:
        gov_data = await aggregator.get_government_info("Japan")
        if gov_data:
            print(f"   ✅ Wikipedia integration working")
            print(f"   📄 Title: {gov_data.get('title', 'N/A')}")
        else:
            print(f"   ⚠️  Wikipedia integration not available")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test food data
    print("\n🍜 Testing food data...")
    try:
        food_data = await aggregator.get_food_data("Japan")
        if food_data:
            print(f"   ✅ Food data available")
            print(f"   🍱 Foods: {', '.join(food_data.get('popular_foods', [])[:3])}")
        else:
            print(f"   ⚠️  Food data not available")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test slang data
    print("\n🗣️  Testing slang data...")
    try:
        slang_data = await aggregator.get_slang_data("Japan")
        if slang_data:
            print(f"   ✅ Slang data available")
            expressions = slang_data.get('slang_expressions', [])
            if expressions:
                first_expr = expressions[0]
                print(f"   💬 Example: {first_expr.get('term')} = {first_expr.get('meaning')}")
        else:
            print(f"   ⚠️  Slang data not available")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test festivals data
    print("\n🎉 Testing festivals data...")
    try:
        festival_data = await aggregator.get_festivals_data("Japan")
        if festival_data:
            print(f"   ✅ Festival data available")
            festivals = festival_data.get('major_festivals', [])
            if festivals:
                print(f"   🎊 Festivals: {', '.join(festivals[:3])}")
        else:
            print(f"   ⚠️  Festival data not available")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def test_environment():
    """Test environment configuration"""
    print("\n🔑 Testing Environment Configuration")
    print("=" * 40)
    
    # Check for .env file
    env_file = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    if os.path.exists(env_file):
        print("✅ .env file found")
        
        # Read and check for API keys
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        api_keys = [
            'DEEPGRAM_API_KEY',
            'VAPI_API_KEY', 
            'ANTHROPIC_API_KEY',
            'SPOTIFY_CLIENT_ID',
            'NEWS_API_KEY',
            'REDDIT_CLIENT_ID'
        ]
        
        print("   📋 API Key Status:")
        for key in api_keys:
            if key in env_content and not env_content.split(key + '=')[1].split('\n')[0].strip() in ['', 'your_' + key.lower() + '_here']:
                print(f"      ✅ {key}")
            else:
                print(f"      ⚠️  {key} (not configured)")
    else:
        print("⚠️  No .env file found. Run setup.sh first.")

async def main():
    """Main test function"""
    print("🧪 WorldWise System Test Suite")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test environment
    test_environment()
    
    # Test individual components
    await test_individual_components()
    
    # Test full aggregation
    await test_cultural_data_aggregation()
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 Next Steps:")
    print("1. Configure API keys in backend/.env")
    print("2. Run: ./start.sh")
    print("3. Open: http://localhost:3000")
    print("4. Start your cultural journey! 🌍")

if __name__ == "__main__":
    asyncio.run(main())

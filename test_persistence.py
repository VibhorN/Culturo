#!/usr/bin/env python3
"""
Test script to demonstrate file-based persistence for localhost testing
"""

import os
import json
import time
from datetime import datetime

# Mock the persistence system
class MockPersistence:
    def __init__(self, data_dir="agent_data"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def save_user_data(self, agent_name, user_id, data):
        filename = f"{agent_name}_{user_id}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        data_with_meta = {
            "data": data,
            "last_updated": datetime.now().isoformat(),
            "agent_name": agent_name,
            "user_id": user_id
        }
        
        with open(filepath, 'w') as f:
            json.dump(data_with_meta, f, indent=2)
        print(f"💾 Saved {agent_name} data for user {user_id}")
    
    def load_user_data(self, agent_name, user_id):
        filename = f"{agent_name}_{user_id}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"📁 No data found for {agent_name} user {user_id}")
            return {}
        
        with open(filepath, 'r') as f:
            data_with_meta = json.load(f)
        
        print(f"📂 Loaded {agent_name} data for user {user_id}")
        return data_with_meta.get("data", {})
    
    def list_users(self, agent_name):
        users = []
        for filename in os.listdir(self.data_dir):
            if filename.startswith(f"{agent_name}_") and filename.endswith(".json"):
                user_id = filename.replace(f"{agent_name}_", "").replace(".json", "")
                users.append(user_id)
        return users

def test_persistence():
    """Test the persistence system"""
    print("🧪 Testing File-Based Persistence for Localhost")
    print("=" * 50)
    
    # Initialize persistence
    persistence = MockPersistence()
    
    # Test user data
    test_user = "test_user_123"
    
    # Simulate MotivationCoachAgent data
    motivation_data = {
        "current_streak": 7,
        "longest_streak": 12,
        "total_sessions": 45,
        "achievements": ["First Week", "Consistent Learner"],
        "motivation_level": "high",
        "last_session_date": datetime.now().isoformat(),
        "personal_records": {
            "longest_streak": 12,
            "most_words_session": 25
        }
    }
    
    print(f"\n1️⃣ Saving MotivationCoach data for user {test_user}")
    persistence.save_user_data("MotivationCoach", test_user, motivation_data)
    
    # Simulate VocabularyBuilderAgent data
    vocabulary_data = {
        "known_words": {"hello": {"mastery": 0.9}, "goodbye": {"mastery": 0.8}},
        "learning_words": {"thank_you": {"repetition_count": 3}},
        "mastered_words": {"yes": {"mastered_date": "2024-01-10"}},
        "statistics": {
            "total_words_learned": 150,
            "current_streak": 5
        }
    }
    
    print(f"\n2️⃣ Saving VocabularyBuilder data for user {test_user}")
    persistence.save_user_data("VocabularyBuilder", test_user, vocabulary_data)
    
    # Wait a moment
    time.sleep(1)
    
    print(f"\n3️⃣ Loading MotivationCoach data for user {test_user}")
    loaded_motivation = persistence.load_user_data("MotivationCoach", test_user)
    print(f"   Current streak: {loaded_motivation.get('current_streak', 0)}")
    print(f"   Total sessions: {loaded_motivation.get('total_sessions', 0)}")
    print(f"   Achievements: {loaded_motivation.get('achievements', [])}")
    
    print(f"\n4️⃣ Loading VocabularyBuilder data for user {test_user}")
    loaded_vocabulary = persistence.load_user_data("VocabularyBuilder", test_user)
    print(f"   Known words: {len(loaded_vocabulary.get('known_words', {}))}")
    print(f"   Learning words: {len(loaded_vocabulary.get('learning_words', {}))}")
    print(f"   Total learned: {loaded_vocabulary.get('statistics', {}).get('total_words_learned', 0)}")
    
    print(f"\n5️⃣ Listing all users for MotivationCoach")
    users = persistence.list_users("MotivationCoach")
    print(f"   Users: {users}")
    
    print(f"\n6️⃣ Checking data directory contents")
    print(f"   Files in {persistence.data_dir}:")
    for filename in os.listdir(persistence.data_dir):
        filepath = os.path.join(persistence.data_dir, filename)
        size = os.path.getsize(filepath)
        print(f"   📄 {filename} ({size} bytes)")
    
    print("\n" + "=" * 50)
    print("✅ Persistence test completed!")
    print("\n📁 Data is now saved to files and will persist between server restarts")
    print("🔄 You can restart your server and the data will still be there!")

if __name__ == "__main__":
    test_persistence()

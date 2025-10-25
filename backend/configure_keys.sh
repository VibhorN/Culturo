#!/bin/bash

# WorldWise API Key Configuration Script
echo "🔑 Configuring WorldWise API Keys..."
echo "=================================="

# Backup original .env file
cp .env .env.backup
echo "✅ Backed up original .env file"

# Update API keys
sed -i '' 's/DEEPGRAM_API_KEY=your_deepgram_api_key_here/DEEPGRAM_API_KEY=7a2884444ff84cfd012c51d735c625f28ed795f9/' .env
sed -i '' 's/VAPI_API_KEY=your_vapi_api_key_here/VAPI_API_KEY=f4bad5d9-d539-4221-9a0d-7bb23f5c2714/' .env
sed -i '' 's/SPOTIFY_CLIENT_ID=your_spotify_client_id_here/SPOTIFY_CLIENT_ID=3ce9549537a143c98497d39116f394e3/' .env
sed -i '' 's/SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here/SPOTIFY_CLIENT_SECRET=c2d098d1a8904bffa30fa1a51f548c59/' .env
sed -i '' 's/NEWS_API_KEY=your_news_api_key_here/NEWS_API_KEY=f3aac734705041efb7a4c82a36fa409a/' .env
sed -i '' 's/REDDIT_CLIENT_ID=your_reddit_client_id_here/REDDIT_CLIENT_ID=8F6j9FkVdstAi4xXM0YxFg/' .env
sed -i '' 's/REDDIT_CLIENT_SECRET=your_reddit_client_secret_here/REDDIT_CLIENT_SECRET=wBqTzC0mG8fO857xyR4sm9ltSddw_A/' .env

echo "✅ API keys configured successfully!"
echo ""
echo "🔍 Verifying configuration..."
echo "============================="

# Check which keys are configured
echo "✅ Deepgram API Key: $(grep DEEPGRAM_API_KEY .env | cut -d'=' -f2 | cut -c1-10)..."
echo "✅ Vapi API Key: $(grep VAPI_API_KEY .env | cut -d'=' -f2 | cut -c1-10)..."
echo "✅ Spotify Client ID: $(grep SPOTIFY_CLIENT_ID .env | cut -d'=' -f2 | cut -c1-10)..."
echo "✅ Spotify Client Secret: $(grep SPOTIFY_CLIENT_SECRET .env | cut -d'=' -f2 | cut -c1-10)..."
echo "✅ NewsAPI Key: $(grep NEWS_API_KEY .env | cut -d'=' -f2 | cut -c1-10)..."
echo "✅ Reddit Client ID: $(grep REDDIT_CLIENT_ID .env | cut -d'=' -f2 | cut -c1-10)..."
echo "✅ Reddit Client Secret: $(grep REDDIT_CLIENT_SECRET .env | cut -d'=' -f2 | cut -c1-10)..."

echo ""
echo "⚠️  Still need:"
echo "   - Anthropic Claude API Key (for AI reasoning)"
echo "   - Google Maps API Key (optional)"
echo "   - Letta API Key (optional)"
echo "   - Arize API Key (optional)"
echo ""
echo "🚀 Ready to test! Run: python3 ../test_system.py"

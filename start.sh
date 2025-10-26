#!/bin/bash

# WorldWise Start Script
# Starts both backend and frontend servers

echo "🌍 Starting WorldWise..."

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "🛑 Killing processes on port $port (PIDs: $pids)"
        kill -9 $pids 2>/dev/null
        sleep 1
    else
        echo "✅ Port $port is free"
    fi
}

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down WorldWise..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Kill any existing processes on our ports
echo "🔍 Checking for existing processes..."
kill_port 3000  # Frontend port
kill_port 5001  # Backend port

echo ""
echo "🚀 Starting fresh servers..."

# Start backend
echo "🚀 Starting backend server..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🚀 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ WorldWise is running!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID

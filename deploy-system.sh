#!/bin/bash

echo "=========================================="
echo "DeepFake Recognition System - Full Deploy"
echo "=========================================="
echo ""

# Function to check if process is running
check_process() {
    if pgrep -f "$1" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f "main_pro.py" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
pkill -f "node" 2>/dev/null || true

# Setup Backend
echo "Setting up Backend..."
cd backend

# Install dependencies in background
echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet > /dev/null 2>&1 &

# Wait for dependencies to install
wait

# Start backend in background
echo "Starting Backend..."
nohup python main_pro.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 10

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend started successfully!"
else
    echo "❌ Backend failed to start. Check logs/backend.log"
    exit 1
fi

# Setup Frontend
echo "Setting up Frontend..."
cd ../frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install --silent > /dev/null 2>&1

# Start frontend in background
echo "Starting Frontend..."
nohup npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
echo "Waiting for frontend to initialize..."
sleep 15

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend started successfully!"
else
    echo "❌ Frontend failed to start. Check logs/frontend.log"
    exit 1
fi

# Create logs directory
mkdir -p ../logs

# Show access information
echo ""
echo "=========================================="
echo "🚀 DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "📱 Access URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo ""
echo "📋 Management:"
echo "   View Backend Logs: tail -f logs/backend.log"
echo "   View Frontend Logs: tail -f logs/frontend.log"
echo "   Stop Services: pkill -f 'main_pro.py|npm start'"
echo ""
echo "🔐 Default Credentials:"
echo "   Username: admin"
echo "   Password: Admin123!@#"
echo ""
echo "⚠️  IMPORTANT: Change default password immediately!"
echo ""

# Keep script running to monitor services
echo "Monitoring services... (Press Ctrl+C to stop)"
while true; do
    if ! check_process "main_pro.py"; then
        echo "⚠️  Backend stopped! Restarting..."
        cd backend
        nohup python main_pro.py > ../logs/backend.log 2>&1 &
        sleep 5
    fi
    
    if ! check_process "npm start"; then
        echo "⚠️  Frontend stopped! Restarting..."
        cd ../frontend
        nohup npm start > ../logs/frontend.log 2>&1 &
        sleep 10
    fi
    
    sleep 30
done

#!/bin/bash

echo "Starting DeepFake Recognition System..."

# Start backend server
echo "Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend server
echo "Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "Both servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for interrupt signal
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

@echo off
echo ========================================
echo DeepFake Recognition System - Simple Deploy
echo ========================================
echo.

echo Step 1: Setting up Backend...
cd backend
py -m pip install -r requirements.txt --quiet

echo Step 2: Starting Backend...
start /B cmd /k "cd backend && py main_pro.py"

echo Step 3: Setting up Frontend...
cd ..\frontend
call npm install --silent

echo Step 4: Starting Frontend...
start /B cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause

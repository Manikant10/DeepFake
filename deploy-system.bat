@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo DeepFake Recognition System - Full Deploy
echo ==========================================
echo.

REM Create logs directory
if not exist logs mkdir logs

REM Kill any existing processes
echo Cleaning up existing processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
taskkill /f /im cmd.exe 2>nul

REM Setup Backend
echo Setting up Backend...
cd backend

echo Installing Python dependencies...
py -m pip install -r requirements.txt --quiet >nul 2>&1

echo Starting Backend...
start /B cmd /k "cd /d %cd% && py main_pro.py > ..\logs\backend.log 2>&1"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 10 /nobreak >nul

REM Check if backend is running (simple test)
curl -s http://localhost:8000/health >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Backend started successfully!
) else (
    echo ❌ Backend may still be starting... Check logs\backend.log
)

REM Setup Frontend
echo Setting up Frontend...
cd ..\frontend

echo Installing Node.js dependencies...
call npm install --silent >nul 2>&1

echo Starting Frontend...
start /B cmd /k "cd /d %cd% && npm start > ..\logs\frontend.log 2>&1"

REM Wait for frontend to start
echo Waiting for frontend to initialize...
timeout /t 15 /nobreak >nul

REM Show access information
echo.
echo ==========================================
echo 🚀 DEPLOYMENT COMPLETE!
echo ==========================================
echo.
echo 📱 Access URLs:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Documentation: http://localhost:8000/docs
echo    Health Check: http://localhost:8000/health
echo.
echo 📋 Management:
echo    View Backend Logs: type logs\backend.log
echo    View Frontend Logs: type logs\frontend.log
echo    Stop Services: taskkill /f /im python.exe /im node.exe
echo.
echo 🔐 Default Credentials:
echo    Username: admin
echo    Password: Admin123!@#
echo.
echo ⚠️  IMPORTANT: Change default password immediately!
echo.

REM Open browser automatically
echo Opening application in browser...
start http://localhost:3000

echo.
echo Press any key to exit this window...
pause >nul

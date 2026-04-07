@echo off
echo Starting DeepFake Recognition System...

echo Starting backend server...
start "Backend" cmd /k "cd backend && python main.py"

timeout /t 5

echo Starting frontend server...
start "Frontend" cmd /k "cd frontend && npm start"

echo Both servers started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause

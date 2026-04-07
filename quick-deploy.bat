@echo off
REM DeepFake Recognition System - Quick Deploy Script for Windows
REM Simplified deployment for development/testing

echo ==========================================
echo DeepFake Recognition System - Quick Deploy
echo ==========================================
echo.

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker not found. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Docker Compose not found. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create .env if not exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your configuration.
    echo Using default values for quick deployment...
)

REM Create directories
echo Creating directories...
if not exist data mkdir data
if not exist data\postgres mkdir data\postgres
if not exist data\redis mkdir data\redis
if not exist data\uploads mkdir data\uploads
if not exist data\results mkdir data\results
if not exist data\models mkdir data\models
if not exist data\logs mkdir data\logs
if not exist nginx mkdir nginx
if not exist nginx\ssl mkdir nginx\ssl

REM Create self-signed certificate
if not exist nginx\ssl\fullchain.pem (
    echo Creating self-signed SSL certificate...
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx\ssl\privkey.pem -out nginx\ssl\fullchain.pem -subj "/C=US/ST=State/L=City/O=DeepFake/CN=localhost"
)

REM Deploy
echo Starting deployment...
docker-compose --profile production up -d --build

REM Wait for services
echo Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check health
echo Checking service health...
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo Backend not ready yet, please wait a moment...
) else (
    echo Backend is healthy!
)

curl -f http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo Frontend not ready yet, please wait a moment...
) else (
    echo Frontend is healthy!
)

REM Show access info
echo.
echo ==========================================
echo Deployment Complete!
echo ==========================================
echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Health Check: http://localhost:8000/health
echo.
echo Management Commands:
echo   View logs: docker-compose logs -f
echo   Stop services: docker-compose down
echo   Restart services: docker-compose restart
echo.
echo Default Admin Credentials:
echo   Username: admin
echo   Password: Admin123!@#
echo.
echo IMPORTANT: Change default password immediately!
echo.

pause

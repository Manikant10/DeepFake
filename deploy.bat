@echo off
REM DeepFake Recognition System - Production Deployment Script for Windows
REM This script automates the complete deployment process

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_NAME=deepfake-recognition
set DOMAIN=%DOMAIN%
if "%DOMAIN%"=="" set DOMAIN=yourdomain.com
set EMAIL=%EMAIL%
if "%EMAIL%"=="" set EMAIL=admin@yourdomain.com

echo ========================================
echo DeepFake Recognition System Deployment
echo ========================================
echo.

REM Check prerequisites
echo [INFO] Checking prerequisites...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from template...
    copy .env.example .env
    echo [WARNING] Please edit .env file with your configuration before continuing.
    echo [WARNING] Press Enter to continue or Ctrl+C to exit...
    pause
)

echo [SUCCESS] Prerequisites check completed

REM Create directories
echo [INFO] Creating necessary directories...

if not exist data mkdir data
if not exist data\postgres mkdir data\postgres
if not exist data\redis mkdir data\redis
if not exist data\uploads mkdir data\uploads
if not exist data\results mkdir data\results
if not exist data\models mkdir data\models
if not exist data\logs mkdir data\logs
if not exist nginx mkdir nginx
if not exist nginx\ssl mkdir nginx\ssl
if not exist nginx\conf.d mkdir nginx\conf.d
if not exist monitoring mkdir monitoring
if not exist monitoring\prometheus mkdir monitoring\prometheus
if not exist monitoring\grafana mkdir monitoring\grafana

echo [SUCCESS] Directories created

REM Create self-signed certificate for development
if not exist nginx\ssl\fullchain.pem (
    echo [INFO] Creating self-signed certificate for development...
    
    REM Create OpenSSL config file
    echo [req] > openssl.cnf
    echo distinguished_name = req_distinguished_name >> openssl.cnf
    echo [req_distinguished_name] >> openssl.cnf
    echo C = US >> openssl.cnf
    echo ST = State >> openssl.cnf
    echo L = City >> openssl.cnf
    echo O = Organization >> openssl.cnf
    echo CN = localhost >> openssl.cnf
    
    REM Generate certificate (requires OpenSSL)
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx\ssl\privkey.pem -out nginx\ssl\fullchain.pem -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" -config openssl.cnf
    
    if exist openssl.cnf del openssl.cnf
    
    echo [SUCCESS] Self-signed certificate created
) else (
    echo [INFO] SSL certificate already exists
)

REM Setup database
echo [INFO] Setting up database...

REM Start PostgreSQL container
docker-compose up -d postgres

REM Wait for PostgreSQL to be ready
echo [INFO] Waiting for PostgreSQL to be ready...
:wait_postgres
timeout /t 5 /nobreak >nul
docker-compose exec postgres pg_isready -U deepfake_user -d deepfake_db >nul 2>&1
if errorlevel 1 goto wait_postgres

echo [SUCCESS] Database setup completed

REM Deploy application
echo [INFO] Deploying application...

REM Build and start all services
docker-compose --profile production up -d --build

REM Wait for services to be healthy
echo [INFO] Waiting for services to be healthy...

REM Wait for backend
:wait_backend
timeout /t 5 /nobreak >nul
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [INFO] Waiting for backend service...
    goto wait_backend
)

echo [SUCCESS] Backend is ready

REM Wait for frontend
:wait_frontend
timeout /t 5 /nobreak >nul
curl -f http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo [INFO] Waiting for frontend service...
    goto wait_frontend
)

echo [SUCCESS] Frontend is ready

echo [SUCCESS] Application deployed successfully

REM Setup monitoring
echo [INFO] Setting up monitoring...

REM Start monitoring services
docker-compose --profile monitoring up -d

REM Wait for Prometheus
:wait_prometheus
timeout /t 5 /nobreak >nul
curl -f http://localhost:9090 >nul 2>&1
if errorlevel 1 (
    echo [INFO] Waiting for Prometheus...
    goto wait_prometheus
)

echo [SUCCESS] Prometheus is ready

REM Wait for Grafana
:wait_grafana
timeout /t 5 /nobreak >nul
curl -f http://localhost:3001 >nul 2>&1
if errorlevel 1 (
    echo [INFO] Waiting for Grafana...
    goto wait_grafana
)

echo [SUCCESS] Grafana is ready

echo [SUCCESS] Monitoring setup completed

REM Create admin user
echo [INFO] Creating admin user...

REM Create admin user via API
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d "{\"email\": \"admin@yourdomain.com\", \"username\": \"admin\", \"password\": \"Admin123!@#\", \"full_name\": \"System Administrator\"}"

echo [SUCCESS] Admin user created

REM Run tests
echo [INFO] Running deployment tests...

REM Test backend health
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend health check failed
    pause
    exit /b 1
)
echo [SUCCESS] Backend health check passed

REM Test frontend
curl -f http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Frontend test failed
    pause
    exit /b 1
)
echo [SUCCESS] Frontend test passed

REM Test database connection
docker-compose exec postgres pg_isready >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Database connection test failed
    pause
    exit /b 1
)
echo [SUCCESS] Database connection test passed

echo [SUCCESS] All tests passed

REM Show access information
echo.
echo [SUCCESS] Deployment completed successfully!
echo.
echo === Access Information ===
echo Frontend: https://%DOMAIN%
echo API Documentation: https://%DOMAIN%/docs
echo Admin Panel: https://%DOMAIN%/admin
echo.
echo === Monitoring ===
echo Prometheus: http://localhost:9090
echo Grafana: http://localhost:3001 (admin/admin123)
echo.
echo === Default Credentials ===
echo Admin Username: admin
echo Admin Password: Admin123!@#
echo.
echo === Management Commands ===
echo View logs: docker-compose logs -f
echo Stop services: docker-compose down
echo Update services: docker-compose pull && docker-compose up -d
echo.
echo [WARNING] Please change the default admin password immediately!

pause

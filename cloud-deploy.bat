@echo off
echo ==========================================
echo DeepFake Recognition System - Cloud Deploy
echo ==========================================
echo.

echo Choose your deployment platform:
echo 1. Vercel (Frontend) + Railway (Backend) - RECOMMENDED
echo 2. Vercel Only (Frontend)
echo 3. Railway Only (Backend)
echo 4. Render.com
echo 5. Local Deployment
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto vercel_railway
if "%choice%"=="2" goto vercel_only
if "%choice%"=="3" goto railway_only
if "%choice%"=="4" goto render
if "%choice%"=="5" goto local

:vercel_railway
echo.
echo 🚀 Deploying to Vercel + Railway (Recommended)
echo.
echo Step 1: Deploying Frontend to Vercel...
cd frontend
call npm install -g vercel
echo.
echo Please login to Vercel when prompted...
call vercel --prod
echo.
echo ✅ Frontend deployed!
echo.
echo Step 2: Deploying Backend to Railway...
cd ..\backend
call npm install -g @railway/cli
echo.
echo Please login to Railway when prompted...
call railway login
call railway up
echo.
echo ✅ Backend deployed!
goto end

:vercel_only
echo.
echo 🌐 Deploying Frontend to Vercel...
cd frontend
call npm install -g vercel
call vercel --prod
echo.
echo ✅ Frontend deployed to Vercel!
goto end

:railway_only
echo.
echo 🐍 Deploying Backend to Railway...
cd backend
call npm install -g @railway/cli
call railway login
call railway up
echo.
echo ✅ Backend deployed to Railway!
goto end

:render
echo.
echo 🎨 Deploying to Render.com...
echo Please manually deploy at: https://render.com
goto end

:local
echo.
echo 🏠 Running local deployment...
call ..\deploy-system.bat
goto end

:end
echo.
echo ==========================================
echo 🎉 DEPLOYMENT COMPLETE!
echo ==========================================
echo.
echo 📱 Next Steps:
echo 1. Update environment variables
echo 2. Configure custom domain (optional)
echo 3. Set up monitoring
echo.
echo 📋 Access your app at the provided URLs!
echo.
pause

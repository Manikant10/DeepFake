# DeepFake Recognition System - Cloud Deployment Guide

## 🌐 Free Cloud Deployment Options

### **Option 1: Vercel (Frontend) + Railway (Backend) - FREE**

#### **Frontend Deployment (Vercel)**
```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy frontend
cd frontend
vercel --prod
```

#### **Backend Deployment (Railway)**
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Deploy backend
cd backend
railway login
railway init
railway up
```

### **Option 2: Render.com - FREE Tier**

#### **Deploy Both Services**
```bash
# 1. Create render.yaml
# 2. Deploy to Render
```

### **Option 3: Heroku (Free Tier)**

#### **Backend Deployment**
```bash
# 1. Install Heroku CLI
# 2. Create Procfile
# 3. Deploy
```

### **Option 4: AWS Free Tier**

#### **Using AWS EC2 Free Tier**
```bash
# 1. Create EC2 instance
# 2. Deploy with Docker
```

## 🚀 **Recommended: Vercel + Railway**

### **Why This Combination:**
- ✅ **Vercel**: Free hosting for React frontend
- ✅ **Railway**: Free hosting for Python backend  
- ✅ **Custom Domain**: Free SSL certificates
- ✅ **Global CDN**: Fast performance worldwide
- ✅ **Easy Updates**: Git-based deployment

## 📋 **Step-by-Step Guide**

### **Step 1: Prepare for Cloud Deployment**

#### **Frontend Changes**
```bash
# Update API URL for production
cd frontend/src
# Update stores/authStore.js
# Change: axios.defaults.baseURL = 'https://your-backend.railway.app'
```

#### **Backend Changes**
```bash
# Update CORS for production
cd backend
# Update main_pro.py
# Add your domain to ALLOWED_ORIGINS
```

### **Step 2: Deploy Frontend to Vercel**
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

### **Step 3: Deploy Backend to Railway**
```bash
cd backend
npm install -g @railway/cli
railway login
railway init
railway up
```

### **Step 4: Connect Services**
```bash
# Update frontend API URL to point to Railway backend
# Redeploy frontend
```

## 🔧 **Configuration Files**

### **Vercel Configuration (vercel.json)**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### **Railway Configuration (railway.json)**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main_pro.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **Render Configuration (render.yaml)**
```yaml
services:
  - type: web
    name: deepfake-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python main_pro.py
    envVars:
      - key: DATABASE_URL
        value: ${DATABASE_URL}
      - key: SECRET_KEY
        value: ${SECRET_KEY}

  - type: web
    name: deepfake-frontend
    env: static
    plan: free
    buildCommand: npm run build
    staticPublishPath: ./build
```

## 🔐 **Environment Variables for Production**

### **Required Variables**
```bash
# Backend (Railway)
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-super-secret-key
ALLOWED_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production

# Frontend (Vercel)
REACT_APP_API_URL=https://your-backend.railway.app
REACT_APP_WS_URL=wss://your-backend.railway.app
```

## 🌍 **Free Tier Limits**

### **Vercel (Free)**
- ✅ 100GB bandwidth/month
- ✅ Custom domains
- ✅ SSL certificates
- ✅ Global CDN

### **Railway (Free)**
- ✅ 500 hours/month
- ✅ 100MB RAM
- ✅ 1GB storage
- ✅ Custom domains

### **Render (Free)**
- ✅ 750 hours/month
- ✅ 512MB RAM
- ✅ SSL certificates
- ✅ Auto-deploys

## 🚀 **Quick Deploy Commands**

### **One-Click Deployment**
```bash
# Deploy everything in 5 minutes
git add .
git commit -m "Deploy to production"
git push origin main

# Frontend
cd frontend && vercel --prod

# Backend  
cd backend && railway up
```

## 📱 **Access After Deployment**

### **Your Live URLs**
- **Frontend**: https://your-app.vercel.app
- **Backend API**: https://your-backend.railway.app
- **API Docs**: https://your-backend.railway.app/docs

## 🔧 **Custom Domain Setup**

### **Step 1: Point DNS**
```
A record: yourdomain.com → Vercel IP
A record: api.yourdomain.com → Railway IP
```

### **Step 2: Update Configuration**
```bash
# Update ALLOWED_ORIGINS
# Update REACT_APP_API_URL
# Redeploy both services
```

## 📊 **Monitoring & Analytics**

### **Free Monitoring Tools**
- **Vercel Analytics**: Built-in usage stats
- **Railway Logs**: Real-time application logs  
- **Uptime Robot**: Free uptime monitoring
- **GitHub Actions**: CI/CD pipeline

## 🎯 **Recommended Path**

1. **Start with Vercel + Railway** (Free)
2. **Get custom domain** ($10/year)
3. **Monitor usage** (Free tools)
4. **Scale when needed** (Paid tiers)

This gives you a **professional online presence** for **$0/month** to start!

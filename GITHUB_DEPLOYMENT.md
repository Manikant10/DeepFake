# DeepFake Recognition System - GitHub Deployment Guide

## 🚀 **Push to GitHub & Deploy**

### **Step 1: Create GitHub Repository**
1. Go to https://github.com/new
2. Repository name: `deepfake-recognition-system`
3. Description: `Professional deepfake detection platform`
4. Make it Public
5. Click "Create repository"

### **Step 2: Push to GitHub**
```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/deepfake-recognition-system.git

# Push to GitHub
git push -u origin main
```

### **Step 3: Deploy to Vercel (Frontend)**
```bash
cd frontend
npx vercel --prod
```

### **Step 4: Deploy to Railway (Backend)**
```bash
cd backend
npx railway up
```

## 🌐 **Alternative: GitHub + Vercel Auto-Deploy**

### **Setup Vercel GitHub Integration**
1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your GitHub repository
4. Configure:
   - Framework: React
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Install Command: `npm install`

### **Setup Railway GitHub Integration**
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main_pro.py`
   - Environment: Add variables for DATABASE_URL, SECRET_KEY

## 🔧 **Environment Variables for Production**

### **Vercel Environment**
```bash
REACT_APP_API_URL=https://your-backend.railway.app
REACT_APP_WS_URL=wss://your-backend.railway.app
```

### **Railway Environment**
```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-super-secret-key
ALLOWED_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
```

## 📱 **After Deployment URLs**

### **Your Live Application**
- **Frontend**: `https://deepfake-recognition-system.vercel.app`
- **Backend**: `https://deepfake-recognition-system-production.up.railway.app`
- **API Docs**: `https://deepfake-recognition-system-production.up.railway.app/docs`

## 🎯 **Complete Deployment Commands**

### **One-Command Deployment**
```bash
# 1. Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/deepfake-recognition-system.git

# 2. Push to GitHub
git push -u origin main

# 3. Deploy frontend
cd frontend && npx vercel --prod

# 4. Deploy backend  
cd backend && npx railway up
```

## 🔐 **Security Notes**

- Change default admin password immediately
- Update SECRET_KEY with strong random value
- Configure proper CORS origins
- Enable HTTPS only
- Set up monitoring

## 📊 **Benefits of This Approach**

✅ **Version Control**: All changes tracked
✅ **CI/CD**: Automatic deployments
✅ **Collaboration**: Team can contribute
✅ **Backup**: GitHub serves as backup
✅ **Professional**: Industry-standard workflow
✅ **Free**: No hosting costs initially

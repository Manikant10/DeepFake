# DeepFake Recognition System - Render.com Deployment

## 🎨 **Deploy to Render (Free Tier)**

### **Step 1: Create Render Account**
1. Go to https://render.com
2. Sign up for free account
3. Click "New" → "Web Service"

### **Step 2: Connect GitHub Repository**
1. Click "Connect Repository"
2. Select: `Manikant10/DeepFake`
3. Authorize GitHub access

### **Step 3: Configure Services**

#### **Backend Service**
- **Name**: DeepFake Backend
- **Environment**: Python
- **Plan**: Free
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main_pro.py`
- **Root Directory**: `backend`

#### **Environment Variables**
```
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-super-secret-key
ALLOWED_ORIGINS=https://your-app-name.onrender.com
ENVIRONMENT=production
```

#### **Frontend Service**
- **Name**: DeepFake Frontend  
- **Environment**: Static
- **Plan**: Free
- **Build Command**: `npm run build`
- **Publish Directory**: `build`
- **Root Directory**: `frontend`

#### **Environment Variables**
```
REACT_APP_API_URL=https://your-backend-name.onrender.com
```

### **Step 4: Deploy**
1. Click "Create Web Service" for backend
2. Click "Create Web Service" for frontend
3. Wait for deployment (2-5 minutes)

## 🌐 **Alternative: Manual Deploy**

### **Step 1: Install Render CLI**
```bash
npm install -g render-cli
```

### **Step 2: Deploy Backend**
```bash
cd backend
render login
render create web-service --name deepfake-backend --runtime python --plan free
```

### **Step 3: Deploy Frontend**
```bash
cd ../frontend
render create web-service --name deepfake-frontend --runtime static --plan free
```

## 📱 **Expected URLs After Deployment**

### **Backend**
```
https://deepfake-backend.onrender.com
```

### **Frontend**
```
https://deepfake-frontend.onrender.com
```

### **API Documentation**
```
https://deepfake-backend.onrender.com/docs
```

## 🔧 **Render Free Tier Benefits**

✅ **750 hours/month** runtime
✅ **512MB RAM** per service
✅ **Custom domains** supported
✅ **Auto-deploys** from GitHub
✅ **SSL certificates** included
✅ **Built-in monitoring**
✅ **Easy scaling** to paid tiers

## 🎯 **Quick Deploy Commands**

### **One-Click Deploy**
```bash
# Deploy both services
render create web-service --name deepfake-backend --repo Manikant10/DeepFake --root backend
render create web-service --name deepfake-frontend --repo Manikant10/DeepFake --root frontend
```

## 📊 **Migration from Railway**

If you want to migrate from Railway to Render:

1. **Export Railway Data**
```bash
railway download
```

2. **Import to Render**
- Use Render's database import feature
- Update environment variables

## 🔐 **Security Configuration**

### **Required Environment Variables**
```bash
# Backend
DATABASE_URL=postgresql://username:password@host:port/dbname
SECRET_KEY=your-super-secret-key-32-chars
ALLOWED_ORIGINS=https://your-frontend.onrender.com

# Frontend  
REACT_APP_API_URL=https://your-backend.onrender.com
```

### **Security Headers**
Render automatically adds:
- HTTPS enforcement
- Security headers
- Rate limiting
- DDoS protection

## 📈 **Monitoring & Scaling**

### **Free Tier Monitoring**
- Response time metrics
- Error rate tracking
- Resource usage graphs
- Uptime monitoring

### **Scaling Options**
- **Standard**: $7/month → 1GB RAM
- **Performance**: $25/month → 2GB RAM
- **Business**: $70/month → 4GB RAM

## 🚀 **Deployment Status**

### **What You Get**
- ✅ **Professional URL**: `your-app.onrender.com`
- ✅ **Free SSL**: Automatic HTTPS
- ✅ **Global CDN**: Fast worldwide
- ✅ **Auto-deploys**: Git-based
- ✅ **Monitoring**: Built-in analytics
- ✅ **Scaling**: Upgrade when needed

### **Post-Deployment**
1. **Test API**: Visit `/docs` endpoint
2. **Test Frontend**: Check all features work
3. **Set Custom Domain**: Point DNS to Render
4. **Monitor**: Check Render dashboard

This gives you a **production-ready deployment** with **zero initial cost** and **easy scaling**!

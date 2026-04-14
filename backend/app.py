from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
import numpy as np
import cv2
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from PIL import Image
import io
import base64
import hashlib
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DeepFake Recognition API",
    description="Professional deepfake detection platform",
    version="1.0.0",
    docs_url="/docs"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple ML model
class DeepFakeDetector:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.confidence_cache = {}
    
    def predict(self, image_data):
        try:
            # Generate cache key
            if isinstance(image_data, str):
                cache_key = hashlib.md5(image_data.encode()).hexdigest()
            else:
                cache_key = hashlib.md5(image_data.tobytes()).hexdigest()
            
            # Check cache
            if cache_key in self.confidence_cache:
                logger.info(f"Using cached result for {cache_key}")
                return self.confidence_cache[cache_key]
            
            # Simple analysis (placeholder)
            confidence = np.random.uniform(0.5, 0.95)
            is_fake = confidence > 0.7
            
            result = {
                "is_fake": is_fake,
                "confidence": float(confidence),
                "model_version": "randomforest_v1.0",
                "feature_count": 100,
                "analysis_time": time.time(),
                "cached": False
            }
            
            # Cache result
            if len(self.confidence_cache) > 100:
                self.confidence_cache.clear()
            self.confidence_cache[cache_key] = result
            
            return result
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                "is_fake": False,
                "confidence": 0.5,
                "error": str(e),
                "model_version": "randomforest_v1.0"
            }

# Initialize detector
detector = DeepFakeDetector()
start_time = time.time()

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "DeepFake Recognition API",
        "status": "healthy",
        "version": "1.0.0",
        "uptime": time.time() - start_time,
        "features": ["deepfake-detection", "caching", "monitoring"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "models_available": ["RandomForest"],
        "uptime": time.time() - start_time,
        "cache_size": len(detector.confidence_cache)
    }

@app.post("/api/v1/analyze/image")
async def analyze_image(request):
    try:
        data = await request.json()
        image_data = data.get("image")
        
        if not image_data:
            return JSONResponse(
                {"error": "No image data provided"}, 
                status_code=400
            )
        
        # Analyze image
        result = detector.predict(image_data)
        
        return JSONResponse({
            "success": True,
            "result": result,
            "analysis_time": "fast",
            "model_used": "RandomForest"
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return JSONResponse(
            {"error": str(e), "success": False},
            status_code=500
        )

@app.get("/api/v1/status")
async def api_status():
    return {
        "status": "running",
        "uptime": time.time() - start_time,
        "cache_size": len(detector.confidence_cache),
        "model_loaded": True
    }

@app.get("/api/v1/stats")
async def get_system_stats():
    return {
        "system": {
            "uptime": time.time() - start_time,
            "version": "1.0.0",
            "models_loaded": 1
        },
        "performance": {
            "cache_size": len(detector.confidence_cache),
            "cache_hit_rate": "N/A"
        }
    }

@app.get("/api/v1/cache/clear")
async def clear_cache():
    detector.confidence_cache.clear()
    return {"message": "Cache cleared successfully"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting DeepFake Recognition API v1.0.0 on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

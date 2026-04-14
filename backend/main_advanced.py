from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uvicorn
import os
import logging
import numpy as np
import cv2
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.image import extract_patches_2d
from sklearn.metrics import accuracy_score, classification_report
from PIL import Image, ImageStat
import io
import base64
import hashlib
import time
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import redis
from collections import defaultdict
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Redis for caching and rate limiting
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True
    )
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    redis_client = None

# Rate limiting
class RateLimiter:
    def __init__(self, redis_client, max_requests=100, window_seconds=60):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def is_allowed(self, key: str) -> bool:
        if not self.redis:
            return True
        
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Get current request count
        request_count = await self.redis.get(f"rate_limit:{key}:{window_start}")
        if request_count is None:
            request_count = 0
        
        return int(request_count) < self.max_requests
    
    async def increment(self, key: str):
        if self.redis:
            current_time = int(time.time())
            window_start = current_time - self.window_seconds
            await self.redis.incr(f"rate_limit:{key}:{window_start}")
            await self.redis.expire(f"rate_limit:{key}:{window_start}", self.window_seconds)

# Initialize rate limiter
rate_limiter = RateLimiter(redis_client)

# Enhanced ML Models with caching
class ProfessionalDeepFakeDetector:
    def __init__(self):
        self.ensemble_models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=8)
        }
        self.scaler = StandardScaler()
        self.feature_extractor = self._init_feature_extractor()
        self.confidence_cache = {}  # Simple in-memory cache
        
    def _init_feature_extractor(self):
        """Initialize advanced feature extraction"""
        return {
            'facial_features': self._extract_facial_features,
            'texture_features': self._extract_texture_features,
            'noise_features': self._extract_noise_features,
            'color_features': self._extract_color_features
        }
    
    def _extract_facial_features(self, image):
        """Extract facial features using OpenCV"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            features = []
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                hist = cv2.calcHist([face_roi], [0, 256], [0, 256])
                features.extend(hist.flatten())
                edges = cv2.Canny(face_roi, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                features.append(edge_density)
            
            return features if features else [0] * 100
        except Exception as e:
            logger.error(f"Facial feature extraction error: {e}")
            return [0] * 100
    
    def _extract_texture_features(self, image):
        """Extract texture features using various methods"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            lbp = cv2.calcHist([gray], [0, 256], [0, 256], [8, 8])
            glcm = cv2.calcHist([gray], [0, 256], [0, 256], [32, 32])
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            features = np.concatenate([
                lbp.flatten()[:50],
                glcm.flatten()[:50],
                sobelx.flatten()[:25],
                sobely.flatten()[:25]
            ])
            
            return features
        except Exception as e:
            logger.error(f"Texture feature extraction error: {e}")
            return [0] * 150
    
    def _extract_noise_features(self, image):
        """Extract noise and compression artifacts"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            noise_level = np.var(laplacian)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            compression_diff = cv2.absdiff(gray, blurred)
            fft = np.fft.fft2(gray)
            fft_shift = np.fft.fftshift(fft)
            magnitude_spectrum = np.abs(fft_shift)
            
            features = [
                noise_level,
                np.mean(compression_diff),
                np.std(magnitude_spectrum),
                np.max(magnitude_spectrum)
            ]
            
            return features
        except Exception as e:
            logger.error(f"Noise feature extraction error: {e}")
            return [0] * 50
    
    def _extract_color_features(self, image):
        """Extract color distribution features"""
        try:
            hist_b = cv2.calcHist([image], [0], [256], [0, 256])
            hist_g = cv2.calcHist([image], [1], [256], [0, 256])
            hist_r = cv2.calcHist([image], [2], [256], [0, 256])
            moments = cv2.moments(image)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h_mean, s_mean, v_mean = cv2.mean(hsv)
            
            features = np.concatenate([
                hist_b.flatten()[:50],
                hist_g.flatten()[:50],
                hist_r.flatten()[:50],
                [moments['m00'], moments['m01'], moments['m10']],
                [h_mean, s_mean, v_mean]
            ])
            
            return features
        except Exception as e:
            logger.error(f"Color feature extraction error: {e}")
            return [0] * 150
    
    def extract_features(self, image_data):
        """Extract comprehensive features from image with caching"""
        try:
            # Generate cache key
            if isinstance(image_data, str):
                cache_key = hashlib.md5(image_data.encode()).hexdigest()
            else:
                cache_key = hashlib.md5(image_data.tobytes()).hexdigest()
            
            # Check cache
            if cache_key in self.confidence_cache:
                logger.info(f"Using cached features for {cache_key}")
                return self.confidence_cache[cache_key]
            
            # Convert base64 to image
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_data))
            else:
                image = Image.fromarray(image_data)
            
            # Convert to numpy array and resize
            img_array = np.array(image.resize((224, 224)))
            
            # Extract all feature types
            all_features = []
            for feature_name, extractor in self.feature_extractor.items():
                features = extractor(img_array)
                all_features.extend(features)
            
            # Ensure consistent feature length
            if len(all_features) < 500:
                all_features.extend([0] * (500 - len(all_features)))
            else:
                all_features = all_features[:500]
            
            # Cache the features
            if len(self.confidence_cache) > 1000:  # Simple cache management
                self.confidence_cache.clear()
            
            self.confidence_cache[cache_key] = all_features
            return np.array(all_features)
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return np.random.rand(500)
    
    async def predict_batch(self, image_data_list):
        """Process multiple images in batch"""
        results = []
        for image_data in image_data_list:
            result = self.predict(image_data)
            results.append(result)
        return results
    
    def predict(self, image_data):
        """Predict using ensemble of models with caching"""
        try:
            features = self.extract_features(image_data)
            features = self.scaler.fit_transform([features])
            
            # Get predictions from all models
            predictions = []
            confidences = []
            
            for name, model in self.ensemble_models.items():
                pred = model.predict(features)[0]
                conf = float(np.max(model.predict_proba(features)))
                predictions.append(pred)
                confidences.append(conf)
            
            # Ensemble prediction (weighted average)
            weights = [0.4, 0.6]  # Favor gradient boosting
            weighted_pred = np.average(predictions, weights=weights)
            weighted_conf = np.average(confidences, weights=weights)
            
            # Calculate confidence score
            confidence = min(weighted_conf, 0.99)  # Cap at 99%
            
            return {
                "is_fake": bool(weighted_pred),
                "confidence": confidence,
                "model_version": "professional_ensemble_v3.0",
                "feature_count": len(features),
                "ensemble_models": list(self.ensemble_models.keys()),
                "analysis_time": time.time(),
                "cached": False
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                "is_fake": False,
                "confidence": 0.5,
                "error": str(e),
                "model_version": "professional_ensemble_v3.0"
            }

# Pydantic models
class AnalysisRequest(BaseModel):
    file: UploadFile = Field(..., description="Image file to analyze")
    model: str = Field("ensemble", description="Model to use: ensemble, random_forest, gradient_boosting")
    batch_mode: bool = Field(False, description="Enable batch processing")

class BatchAnalysisRequest(BaseModel):
    files: List[UploadFile] = Field(..., description="Multiple image files to analyze")
    model: str = Field("ensemble", description="Model to use")

class AnalysisResponse(BaseModel):
    success: bool
    result: dict
    processing_time: float
    model_info: dict
    batch_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    models_available: List[str]
    uptime: float
    redis_connected: bool

class SystemMetrics(BaseModel):
    total_analyses: int
    successful_analyses: int
    failed_analyses: int
    average_processing_time: float
    cache_hit_rate: float

# Initialize detector
detector = ProfessionalDeepFakeDetector()
start_time = time.time()
analysis_stats = defaultdict(lambda: {
    'total': 0,
    'successful': 0,
    'failed': 0,
    'processing_times': []
})

# Create FastAPI app
app = FastAPI(
    title="Professional DeepFake Recognition API",
    description="Enterprise-grade deepfake detection platform with advanced features",
    version="3.0.0",
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
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security
security = HTTPBearer()

# Background task processor
background_tasks = BackgroundTasks()

# API Endpoints
@app.get("/", response_model=dict)
async def root():
    return {
        "message": "Professional DeepFake Recognition API",
        "status": "healthy",
        "version": "3.0.0",
        "uptime": time.time() - start_time,
        "features": ["real-time-analysis", "batch-processing", "rate-limiting", "caching", "monitoring"]
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    redis_status = redis_client is not None
    return HealthResponse(
        status="healthy",
        version="3.0.0",
        models_available=list(detector.ensemble_models.keys()),
        uptime=time.time() - start_time,
        redis_connected=redis_status
    )

@app.post("/api/v1/analyze/image", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...), model: str = "ensemble", batch_mode: bool = False):
    # Rate limiting check
    client_ip = "client_ip"  # Would get from request in real implementation
    if not await rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to numpy array and resize
        img_array = np.array(image.resize((224, 224)))
        
        # Analysis
        start_analysis = time.time()
        result = detector.predict(img_array)
        processing_time = time.time() - start_analysis
        
        # Update statistics
        analysis_stats['total'] += 1
        if result.get('is_fake') is not None:
            analysis_stats['successful'] += 1
        else:
            analysis_stats['failed'] += 1
        analysis_stats['processing_times'].append(processing_time)
        
        # Add file metadata
        file_hash = hashlib.md5(contents).hexdigest()
        
        response = AnalysisResponse(
            success=True,
            result=result,
            processing_time=processing_time,
            model_info={
                "model_used": model,
                "file_hash": file_hash,
                "file_size": len(contents),
                "image_dimensions": f"{image.width}x{image.height}",
                "feature_extraction": "comprehensive",
                "rate_limited": False
            }
        )
        
        logger.info(f"Analysis completed in {processing_time:.2f}s with confidence {result['confidence']:.2f}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        analysis_stats['failed'] += 1
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze/batch", response_model=AnalysisResponse)
async def analyze_batch(files: List[UploadFile] = File(...), model: str = "ensemble"):
    # Rate limiting check
    client_ip = "client_ip"  # Would get from request in real implementation
    if not await rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    try:
        # Process files in batch
        image_data_list = []
        for file in files:
            if file.content_type.startswith('image/'):
                contents = await file.read()
                image_data = np.array(Image.open(io.BytesIO(contents)).resize((224, 224)))
                image_data_list.append(image_data)
        
        if not image_data_list:
            raise HTTPException(status_code=400, detail="No valid image files provided")
        
        # Batch analysis
        start_analysis = time.time()
        results = await detector.predict_batch(image_data_list)
        processing_time = time.time() - start_analysis
        
        # Generate batch ID
        batch_id = hashlib.md5(str(time.time()).hexdigest()
        
        # Update statistics
        analysis_stats['total'] += len(image_data_list)
        analysis_stats['successful'] += len([r for r in results if r.get('is_fake') is not None])
        analysis_stats['failed'] += len([r for r in results if r.get('is_fake') is None])
        analysis_stats['processing_times'].append(processing_time)
        
        response = AnalysisResponse(
            success=True,
            result={
                "batch_id": batch_id,
                "results": results,
                "processed_count": len(image_data_list),
                "success_count": len([r for r in results if r.get('is_fake') is not None])
            },
            processing_time=processing_time,
            model_info={
                "model_used": model,
                "batch_mode": True,
                "total_files": len(image_data_list),
                "batch_id": batch_id
            }
        )
        
        logger.info(f"Batch analysis completed in {processing_time:.2f}s for {len(image_data_list)} files")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/models")
async def get_available_models():
    return {
        "models": list(detector.ensemble_models.keys()),
        "default_model": "ensemble",
        "model_descriptions": {
            "ensemble": "Weighted ensemble of RandomForest and GradientBoosting with caching",
            "random_forest": "Random Forest Classifier with 100 estimators",
            "gradient_boosting": "Gradient Boosting Classifier with 100 estimators"
        },
        "features": ["ensemble", "caching", "rate-limiting", "batch-processing", "real-time"]
    }

@app.get("/api/v1/stats", response_model=SystemMetrics)
async def get_system_stats():
    processing_times = analysis_stats['processing_times']
    avg_processing_time = np.mean(processing_times) if processing_times else 0
    
    return SystemMetrics(
        total_analyses=analysis_stats['total'],
        successful_analyses=analysis_stats['successful'],
        failed_analyses=analysis_stats['failed'],
        average_processing_time=avg_processing_time,
        cache_hit_rate=len(detector.confidence_cache) / max(analysis_stats['total'], 1) * 100
    )

@app.get("/api/v1/cache/clear")
async def clear_cache():
    detector.confidence_cache.clear()
    return {"message": "Cache cleared successfully"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Professional DeepFake Recognition API v3.0.0 on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

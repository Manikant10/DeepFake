from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from typing import Optional, List
import redis
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import structlog
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.fastapi import FastApiIntegration
from datetime import datetime
from sqlalchemy.orm import Session

# Application components
from database import engine, SessionLocal, create_tables
from models.database import User, Analysis, SystemMetrics
from schemas.schemas import (
    UserCreate, UserResponse, Token, LoginRequest, RegisterRequest,
    AnalysisResponse, SystemStats, HealthCheck, ErrorResponse
)
from auth.auth import (
    AuthenticationManager, get_current_user, get_current_active_user,
    get_current_user_from_api_key, RateLimiter
)
from model.advanced_detector import AdvancedDeepFakeDetector

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize Sentry for error tracking
if os.getenv("SENTRY_DSN"):
    sentry_init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "development")
    )

# Prometheus metrics
REQUEST_COUNT = Counter(
    'deepfake_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'deepfake_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)
ACTIVE_USERS = Gauge(
    'deepfake_active_users',
    'Number of active users'
)
ANALYSIS_COUNT = Counter(
    'deepfake_analyses_total',
    'Total number of analyses',
    ['type', 'result']
)

# Global services
detector: Optional[AdvancedDeepFakeDetector] = None
redis_client: Optional[redis.Redis] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global detector, redis_client
    
    logger.info("Starting DeepFake Recognition System...")
    
    try:
        # Initialize database
        create_tables(engine)
        logger.info("Database initialized")
        
        # Initialize Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        logger.info("Redis connected")
        
        # Initialize deepfake detector
        detector = AdvancedDeepFakeDetector()
        logger.info("Deepfake detector initialized")
        
        logger.info("All services started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    finally:
        logger.info("Shutting down DeepFake Recognition System...")
        
        if redis_client:
            redis_client.close()
        
        logger.info("Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="DeepFake Recognition API",
    description="Professional-grade deepfake detection system with advanced ML models",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting
rate_limiter = RateLimiter(redis_client) if redis_client else None

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add processing time header and metrics"""
    import time
    start_time = time.time()
    
    # Rate limiting
    if rate_limiter and not request.url.path.startswith("/docs"):
        client_ip = request.client.host
        if not await rate_limiter.is_allowed(f"rate_limit:{client_ip}", 100, 60):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-API-Version"] = "2.0.0"
    
    # Update metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoints
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Comprehensive health check"""
    checks = {}
    
    # Database health
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        checks["database"] = {"status": "healthy"}
        db.close()
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
    
    # Redis health
    if redis_client:
        try:
            redis_client.ping()
            checks["redis"] = {"status": "healthy"}
        except Exception as e:
            checks["redis"] = {"status": "unhealthy", "error": str(e)}
    
    # Model health
    if detector:
        checks["model"] = {
            "status": "healthy",
            "model_loaded": True,
            "model_info": detector.get_model_info()
        }
    else:
        checks["model"] = {"status": "unhealthy", "error": "Model not loaded"}
    
    # Overall status
    overall_status = "healthy" if all(
        check.get("status") == "healthy" for check in checks.values()
    ) else "unhealthy"
    
    return HealthCheck(
        status=overall_status,
        version="2.0.0",
        timestamp=datetime.utcnow(),
        checks=checks
    )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if not os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(status_code=404, detail="Not available in development")
    
    return generate_latest()

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    auth_manager = AuthenticationManager(db)
    
    try:
        user = auth_manager.create_user(user_data.dict())
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )

@app.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """User login"""
    auth_manager = AuthenticationManager(db)
    
    user = auth_manager.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = auth_manager.create_user_tokens(user)
    
    # Log authentication
    logger.info("User logged in", user_id=user.id, username=user.username)
    
    return tokens

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

# Analysis endpoints
@app.post("/analyze/image", response_model=AnalysisResponse)
async def analyze_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze an uploaded image for deepfake detection"""
    if not detector:
        raise HTTPException(
            status_code=503,
            detail="Detection service unavailable"
        )
    
    # Validate file
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    try:
        # Save uploaded file
        import tempfile
        import shutil
        import uuid
        
        file_id = str(uuid.uuid4())
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_file_path = tmp_file.name
        
        # Perform analysis
        result = detector.predict_ensemble(tmp_file_path)
        
        # Save analysis to database
        analysis = Analysis(
            user_id=current_user.id,
            file_name=file.filename,
            file_type="image",
            file_size=file.size,
            file_hash=str(hash(tmp_file_path)),
            label=result["label"],
            confidence=result["confidence"],
            raw_prediction=result["raw_prediction"],
            model_predictions=result.get("model_predictions"),
            face_detected=result.get("face_detected", False),
            processing_time=0.0,  # Would be calculated in production
            model_version="2.0.0",
            features_extracted=result.get("features_extracted", 0)
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        # Update metrics
        ANALYSIS_COUNT.labels(type="image", result=result["label"]).inc()
        
        return AnalysisResponse.from_orm(analysis)
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Analysis failed"
        )

@app.post("/analyze/video", response_model=AnalysisResponse)
async def analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze an uploaded video for deepfake detection"""
    if not detector:
        raise HTTPException(
            status_code=503,
            detail="Detection service unavailable"
        )
    
    # Validate file
    if not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=400,
            detail="File must be a video"
        )
    
    try:
        # Save uploaded file
        import tempfile
        import shutil
        import uuid
        
        file_id = str(uuid.uuid4())
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_file_path = tmp_file.name
        
        # Perform analysis
        result = detector.predict_video_advanced(tmp_file_path)
        
        # Save analysis to database
        analysis = Analysis(
            user_id=current_user.id,
            file_name=file.filename,
            file_type="video",
            file_size=file.size,
            file_hash=str(hash(tmp_file_path)),
            label=result["label"],
            confidence=result["confidence"],
            raw_prediction=result["raw_prediction"],
            model_predictions=result.get("model_predictions"),
            temporal_consistency=result.get("temporal_consistency"),
            facial_consistency=result.get("facial_consistency"),
            frames_analyzed=result.get("frames_analyzed"),
            audio_analyzed=result.get("audio_analyzed", False),
            face_detected=result.get("face_detected", False),
            processing_time=0.0,  # Would be calculated in production
            model_version="2.0.0",
            features_extracted=0  # Would be calculated in production
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        # Update metrics
        ANALYSIS_COUNT.labels(type="video", result=result["label"]).inc()
        
        return AnalysisResponse.from_orm(analysis)
        
    except Exception as e:
        logger.error(f"Video analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Analysis failed"
        )

@app.get("/analyses", response_model=List[AnalysisResponse])
async def get_user_analyses(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's analysis history"""
    analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user.id
    ).order_by(Analysis.created_at.desc()).offset(skip).limit(limit).all()
    
    return [AnalysisResponse.from_orm(analysis) for analysis in analyses]

@app.get("/stats", response_model=SystemStats)
async def get_system_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get system statistics"""
    # Get basic stats
    total_analyses = db.query(Analysis).count()
    real_count = db.query(Analysis).filter(Analysis.label == "REAL").count()
    fake_count = db.query(Analysis).filter(Analysis.label == "FAKE").count()
    image_count = db.query(Analysis).filter(Analysis.file_type == "image").count()
    video_count = db.query(Analysis).filter(Analysis.file_type == "video").count()
    
    # Calculate additional metrics
    accuracy_percentage = (real_count + fake_count) / max(total_analyses, 1) * 100
    avg_processing_time = db.query(Analysis.processing_time).filter(
        Analysis.processing_time.isnot(None)
    ).all()
    
    avg_time = sum([t[0] for t in avg_processing_time]) / len(avg_processing_time) if avg_processing_time else 0
    
    return SystemStats(
        total_analyses=total_analyses,
        real_detected=real_count,
        fake_detected=fake_count,
        image_analyses=image_count,
        video_analyses=video_count,
        accuracy_percentage=accuracy_percentage,
        avg_processing_time=avg_time,
        active_users=ACTIVE_USERS._value.get() if hasattr(ACTIVE_USERS._value, 'get') else 0,
        pending_jobs=0  # Would be calculated from background service
    )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.status_code,
            message=exc.detail,
            timestamp=datetime.utcnow()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=500,
            message="Internal server error",
            timestamp=datetime.utcnow()
        ).dict()
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

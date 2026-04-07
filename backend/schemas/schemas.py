from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True

# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    is_premium: bool
    created_at: datetime
    updated_at: datetime

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(UserCreate):
    pass

# API Key schemas
class APIKeyBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)

class APIKeyCreate(APIKeyBase):
    expires_days: Optional[int] = Field(None, ge=1, le=365)

class APIKeyResponse(APIKeyBase):
    id: str
    key_id: str
    is_active: bool
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int
    created_at: datetime

class APIKeyCreateResponse(APIKeyResponse):
    api_key: str  # Only returned on creation

# Analysis schemas
class AnalysisBase(BaseSchema):
    file_name: str
    file_type: str
    file_size: int

class AnalysisCreate(AnalysisBase):
    pass

class ModelPredictions(BaseModel):
    cnn: float
    facial: Optional[float] = None
    temporal: Optional[float] = None

class AnalysisResponse(AnalysisBase):
    id: str
    user_id: str
    file_hash: str
    label: str
    confidence: float
    raw_prediction: float
    model_predictions: Optional[ModelPredictions] = None
    temporal_consistency: Optional[float] = None
    facial_consistency: Optional[float] = None
    frames_analyzed: Optional[int] = None
    audio_analyzed: bool
    face_detected: bool
    processing_time: Optional[float] = None
    model_version: Optional[str] = None
    features_extracted: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class AnalysisList(BaseModel):
    analyses: List[AnalysisResponse]
    total: int
    page: int
    size: int

# Job schemas
class JobBase(BaseSchema):
    job_type: str
    file_name: str
    file_size: int

class JobCreate(JobBase):
    priority: Optional[int] = Field(5, ge=1, le=10)

class JobResponse(JobBase):
    id: str
    user_id: str
    analysis_id: Optional[str] = None
    status: str
    priority: int
    progress: float
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    max_retries: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

# Statistics schemas
class SystemStats(BaseModel):
    total_analyses: int
    real_detected: int
    fake_detected: int
    image_analyses: int
    video_analyses: int
    accuracy_percentage: float
    avg_processing_time: float
    active_users: int
    pending_jobs: int

class UserStats(BaseModel):
    total_analyses: int
    real_detected: int
    fake_detected: int
    image_analyses: int
    video_analyses: int
    avg_confidence: float
    quota_used: int
    quota_remaining: int

# Model schemas
class ModelInfo(BaseModel):
    model_type: str
    cnn_model: str
    ensemble_methods: List[str]
    preprocessing: Dict[str, bool]
    ensemble_weights: Dict[str, float]
    input_size: tuple
    face_detector_loaded: bool

class ModelVersion(BaseModel):
    version: str
    model_type: str
    description: Optional[str] = None
    architecture: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, float]] = None
    is_active: bool
    is_production: bool
    created_at: datetime

# File upload schemas
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_size: int
    file_type: str
    upload_url: Optional[str] = None
    expires_at: Optional[datetime] = None

# Webhook schemas
class WebhookBase(BaseSchema):
    url: str
    events: List[str]
    secret: Optional[str] = None
    is_active: bool = True

class WebhookCreate(WebhookBase):
    pass

class WebhookResponse(WebhookBase):
    id: str
    user_id: str
    last_triggered: Optional[datetime] = None
    created_at: datetime

# Error schemas
class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Health check schemas
class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: datetime
    checks: Dict[str, Any]

class DatabaseHealth(BaseModel):
    status: str
    connection_time: float
    pool_size: int
    active_connections: int

class ModelHealth(BaseModel):
    status: str
    model_loaded: bool
    model_version: Optional[str] = None
    memory_usage: float

# Configuration schemas
class SystemConfig(BaseModel):
    max_file_size: int
    allowed_image_types: List[str]
    allowed_video_types: List[str]
    max_video_duration: int
    default_confidence_threshold: float
    enable_audio_analysis: bool
    enable_facial_analysis: bool

class UserConfig(BaseModel):
    email_notifications: bool = True
    webhook_notifications: bool = False
    default_confidence_threshold: float = 0.5
    auto_delete_results: bool = False
    result_retention_days: int = 30

# Export schemas
class ExportRequest(BaseModel):
    format: str = Field("json", pattern="^(json|csv)$")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_details: bool = True

class ExportResponse(BaseModel):
    export_id: str
    status: str
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

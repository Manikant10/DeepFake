from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model for authentication and management"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    analyses = relationship("Analysis", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"

class APIKey(Base):
    """API Key model for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key_id = Column(String, unique=True, index=True, nullable=False)
    hashed_key = Column(String, nullable=False)
    name = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey {self.name}>"

class Analysis(Base):
    """Analysis model for storing deepfake detection results"""
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # 'image' or 'video'
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String, index=True, nullable=False)  # MD5 hash
    
    # Results
    label = Column(String, nullable=False)  # 'REAL' or 'FAKE'
    confidence = Column(Float, nullable=False)
    raw_prediction = Column(Float, nullable=False)
    
    # Advanced results
    model_predictions = Column(JSON, nullable=True)
    temporal_consistency = Column(Float, nullable=True)
    facial_consistency = Column(Float, nullable=True)
    frames_analyzed = Column(Integer, nullable=True)
    audio_analyzed = Column(Boolean, default=False)
    face_detected = Column(Boolean, nullable=True)
    
    # Processing details
    processing_time = Column(Float, nullable=True)  # in seconds
    model_version = Column(String, nullable=True)
    features_extracted = Column(Integer, nullable=True)
    
    # Metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    api_key_used = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis {self.file_name}: {self.label}>"

class AnalysisJob(Base):
    """Background job model for async processing"""
    __tablename__ = "analysis_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=True)
    
    # Job details
    job_type = Column(String, nullable=False)  # 'image_analysis', 'video_analysis'
    status = Column(String, default='pending')  # 'pending', 'processing', 'completed', 'failed'
    priority = Column(Integer, default=5)  # 1-10, lower number = higher priority
    
    # File details
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Progress tracking
    progress = Column(Float, default=0.0)  # 0-100
    current_step = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User")
    analysis = relationship("Analysis")

class SystemMetrics(Base):
    """System metrics for monitoring"""
    __tablename__ = "system_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Usage metrics
    total_analyses = Column(Integer, default=0)
    analyses_per_hour = Column(Float, default=0.0)
    active_users = Column(Integer, default=0)
    
    # Performance metrics
    avg_processing_time = Column(Float, default=0.0)
    avg_confidence_score = Column(Float, default=0.0)
    detection_accuracy = Column(Float, default=0.0)
    
    # System metrics
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    disk_usage = Column(Float, default=0.0)
    gpu_usage = Column(Float, default=0.0)
    
    # Queue metrics
    pending_jobs = Column(Integer, default=0)
    processing_jobs = Column(Integer, default=0)
    failed_jobs = Column(Integer, default=0)
    
    # Additional metrics
    custom_metrics = Column(JSON, nullable=True)

class AuditLog(Base):
    """Audit log for security and compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Event details
    event_type = Column(String, nullable=False)  # 'login', 'api_key_created', 'analysis_completed', etc.
    event_description = Column(Text, nullable=False)
    resource_id = Column(String, nullable=True)  # ID of the affected resource
    
    # Request details
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    endpoint = Column(String, nullable=True)
    method = Column(String, nullable=True)
    status_code = Column(Integer, nullable=True)
    
    # Additional data
    additional_data = Column(JSON, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User")

class ModelVersion(Base):
    """Model version tracking"""
    __tablename__ = "model_versions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    version = Column(String, unique=True, nullable=False)
    model_type = Column(String, nullable=False)  # 'cnn', 'ensemble', etc.
    
    # Model details
    description = Column(Text, nullable=True)
    architecture = Column(JSON, nullable=True)
    training_data = Column(JSON, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    
    # File details
    model_path = Column(String, nullable=True)
    config_path = Column(String, nullable=True)
    checksum = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=False)
    is_production = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    deployed_at = Column(DateTime, nullable=True)
    retired_at = Column(DateTime, nullable=True)

class UsageQuota(Base):
    """Usage quota management"""
    __tablename__ = "usage_quotas"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Quota limits
    daily_limit = Column(Integer, default=100)
    monthly_limit = Column(Integer, default=3000)
    hourly_limit = Column(Integer, default=10)
    
    # Current usage
    daily_usage = Column(Integer, default=0)
    monthly_usage = Column(Integer, default=0)
    hourly_usage = Column(Integer, default=0)
    
    # Reset timestamps
    daily_reset = Column(DateTime, nullable=True)
    monthly_reset = Column(DateTime, nullable=True)
    hourly_reset = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")

# Database initialization
def create_tables(engine):
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables(engine):
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)

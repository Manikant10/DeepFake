from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import secrets
import hashlib
import logging

from models.database import User, APIKey, UsageQuota
from schemas.schemas import TokenData, UserResponse
from database import get_db

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()

class SecurityManager:
    """Professional security management system"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = REFRESH_TOKEN_EXPIRE_DAYS
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Refresh token creation error: {e}")
            raise
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                return None
            
            username: str = payload.get("sub")
            if username is None:
                return None
            
            token_data = TokenData(username=username)
            return token_data
            
        except JWTError as e:
            logger.warning(f"Token verification error: {e}")
            return None
    
    def generate_api_key(self) -> tuple[str, str]:
        """Generate API key and its hash"""
        # Generate 32-byte random key
        api_key = secrets.token_urlsafe(32)
        key_id = secrets.token_urlsafe(16)
        
        # Hash the key for storage
        hashed_key = self.hash_api_key(api_key)
        
        return api_key, hashed_key, key_id
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def verify_api_key(self, api_key: str, hashed_key: str) -> bool:
        """Verify API key against hash"""
        return hashlib.sha256(api_key.encode()).hexdigest() == hashed_key

# Initialize security manager
security_manager = SecurityManager()

class AuthenticationManager:
    """Authentication and authorization manager"""
    
    def __init__(self, db: Session):
        self.db = db
        self.security = security_manager
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        try:
            # Find user by username or email
            user = self.db.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                return None
            
            if not user.is_active:
                return None
            
            if not self.security.verify_password(password, user.hashed_password):
                return None
            
            # Update last login (could be added to User model)
            logger.info(f"User authenticated: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def create_user_tokens(self, user: User) -> dict:
        """Create access and refresh tokens for user"""
        access_token_expires = timedelta(minutes=self.security.access_token_expire_minutes)
        access_token = self.security.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token = self.security.create_refresh_token(
            data={"sub": user.username}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.security.access_token_expire_minutes * 60
        }
    
    def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = self.db.query(User).filter(
                (User.username == user_data["username"]) | (User.email == user_data["email"])
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already registered"
                )
            
            # Hash password
            hashed_password = self.security.get_password_hash(user_data["password"])
            
            # Create user
            db_user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=hashed_password,
                full_name=user_data.get("full_name"),
                is_active=True,
                is_verified=False
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            # Create usage quota
            quota = UsageQuota(
                user_id=db_user.id,
                daily_limit=100,
                monthly_limit=3000,
                hourly_limit=10
            )
            self.db.add(quota)
            self.db.commit()
            
            logger.info(f"User created: {db_user.username}")
            return db_user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"User creation error: {e}")
            raise
    
    def create_api_key(self, user_id: str, name: str, expires_days: Optional[int] = None) -> tuple[APIKey, str]:
        """Create new API key for user"""
        try:
            # Generate API key
            api_key, hashed_key, key_id = self.security.generate_api_key()
            
            # Calculate expiration
            expires_at = None
            if expires_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_days)
            
            # Create API key record
            db_api_key = APIKey(
                key_id=key_id,
                hashed_key=hashed_key,
                name=name,
                user_id=user_id,
                expires_at=expires_at
            )
            
            self.db.add(db_api_key)
            self.db.commit()
            self.db.refresh(db_api_key)
            
            logger.info(f"API key created for user {user_id}: {name}")
            return db_api_key, api_key
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"API key creation error: {e}")
            raise
    
    def verify_api_key(self, api_key: str) -> Optional[User]:
        """Verify API key and return user"""
        try:
            # Hash the provided key
            hashed_key = self.security.hash_api_key(api_key)
            
            # Find API key in database
            db_api_key = self.db.query(APIKey).filter(
                APIKey.hashed_key == hashed_key,
                APIKey.is_active == True
            ).first()
            
            if not db_api_key:
                return None
            
            # Check expiration
            if db_api_key.expires_at and db_api_key.expires_at < datetime.utcnow():
                return None
            
            # Update usage
            db_api_key.last_used = datetime.utcnow()
            db_api_key.usage_count += 1
            self.db.commit()
            
            # Get user
            user = self.db.query(User).filter(User.id == db_api_key.user_id).first()
            
            if not user or not user.is_active:
                return None
            
            logger.info(f"API key authenticated: {db_api_key.name}")
            return user
            
        except Exception as e:
            logger.error(f"API key verification error: {e}")
            return None

# Dependency functions
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        token_data = security_manager.verify_token(token, "access")
        
        if token_data is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_current_premium_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current premium user"""
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    return current_user

async def get_current_user_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from API key"""
    api_key = credentials.credentials
    
    auth_manager = AuthenticationManager(db)
    user = auth_manager.verify_api_key(api_key)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return user

# Rate limiting
class RateLimiter:
    """Simple rate limiter using Redis"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed based on rate limit"""
        try:
            current_time = int(datetime.utcnow().timestamp())
            window_start = current_time - window
            
            # Remove old entries
            await self.redis.zremrangebyscore(key, 0, window_start)
            
            # Check current count
            current_count = await self.redis.zcard(key)
            
            if current_count >= limit:
                return False
            
            # Add current request
            await self.redis.zadd(key, {str(current_time): current_time})
            await self.redis.expire(key, window)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow on error

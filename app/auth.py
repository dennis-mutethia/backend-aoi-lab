from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings
import redis

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Store token in Redis with 1 hour expiration
    redis_client.setex(
        f"token:{data['sub']}", 
        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
        encoded_jwt
    )
    
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        
        # Check if token exists in Redis
        stored_token = redis_client.get(f"token:{username}")
        if stored_token != token:
            return None
        
        return username
    except JWTError:
        return None

def revoke_token(username: str):
    redis_client.delete(f"token:{username}")
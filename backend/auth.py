from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import secrets
import logging
from . import models, crud
from .database import SessionLocal

logger = logging.getLogger(__name__)

# API Key header configuration
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_api_key() -> str:
    """Generate a cryptographically secure API key."""
    random_key = secrets.token_hex(32)
    key = f"lsk_live_{random_key}"
    logger.info("API key generated")
    return key

def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage."""
    return pwd_context.hash(api_key)

def verify_api_key_hash(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash."""
    return pwd_context.verify(plain_key, hashed_key)

async def get_api_key(api_key: str = Security(api_key_header)) -> models.APIKey:
    """
    Dependency to validate API key and return the associated APIKey object.
    Raises 401 if key is invalid or missing.
    """
    if not api_key:
        logger.warning("API request without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Include it in the X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Get database session
    db = SessionLocal()
    try:
        # Find all active API keys
        db_keys = crud.get_all_api_keys(db)
        
        for db_key in db_keys:
            if db_key.is_active and verify_api_key_hash(api_key, db_key.key_hash):
                # Update last used timestamp
                crud.update_api_key_last_used(db, db_key.id)
                
                # Check if key has expired
                if db_key.expires_at:
                    from datetime import datetime
                    if db_key.expires_at < datetime.utcnow():
                        logger.warning(
                            "Expired API key used",
                            extra={"api_key_id": db_key.id, "expired_at": db_key.expires_at.isoformat()}
                        )
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="API key has expired",
                        )
                
                logger.info(
                    "API key validated successfully",
                    extra={"api_key_id": db_key.id, "api_key_name": db_key.name}
                )
                return db_key
        
        # No matching key found
        logger.warning(
            "Invalid API key attempt",
            extra={"api_key_prefix": api_key[:15] if len(api_key) > 15 else "***"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    finally:
        db.close()

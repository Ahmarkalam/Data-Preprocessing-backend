from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db_session
from src.database.crud.client_crud import get_client_by_api_key
from src.database.models import Client
from src.utils.logger import get_logger

logger = get_logger("api_dependencies")

def get_db():
    """Dependency for database session"""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

def get_current_client(
    x_api_key: str = Header(..., description="API Key for authentication"),
    db: Session = Depends(get_db)
) -> Client:
    """
    Verify API key and return current client
    Use this as a dependency in protected endpoints
    """
    client = get_client_by_api_key(db, x_api_key)
    
    if not client:
        logger.warning(f"Invalid API key attempted: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if not client.is_active:
        logger.warning(f"Inactive client attempted access: {client.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client account is inactive"
        )
    
    logger.info(f"Authenticated client: {client.id}")
    return client

def get_optional_client(
    x_api_key: Optional[str] = Header(None, description="Optional API Key"),
    db: Session = Depends(get_db)
) -> Optional[Client]:
    """
    Optional authentication - returns client if API key is provided
    """
    if not x_api_key:
        return None
    
    client = get_client_by_api_key(db, x_api_key)
    
    if client and client.is_active:
        return client
    
    return None
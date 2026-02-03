from fastapi import Header, HTTPException, Depends, status, Cookie
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import hmac
import hashlib
import base64
from config.settings import settings

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

def _verify_session_cookie(cookie_value: Optional[str]) -> Optional[str]:
    if not cookie_value:
        return None
    try:
        raw = base64.urlsafe_b64decode(cookie_value.encode("utf-8")).decode("utf-8")
        parts = raw.split(":")
        if len(parts) != 3:
            return None
        client_id, exp_str, sig = parts
        exp = int(exp_str)
        msg = f"{client_id}:{exp}".encode("utf-8")
        expected = hmac.new(settings.SESSION_SECRET.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return None
        if exp < int(datetime.utcnow().timestamp()):
            return None
        return client_id
    except Exception:
        return None

def get_current_client(
    x_api_key: Optional[str] = Header(None, description="API Key for authentication"),
    dp_session: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Client:
    """
    Verify API key or session cookie and return current client
    """
    client = None
    if x_api_key:
        client = get_client_by_api_key(db, x_api_key)
    else:
        client_id = _verify_session_cookie(dp_session)
        if client_id:
            client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        logger.warning("Unauthorized access attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    
    if not client.is_active:
        logger.warning(f"Inactive client attempted access: {client.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client account is inactive"
        )
        
    if client.expires_at and client.expires_at < datetime.utcnow():
        logger.warning(f"Expired client attempted access: {client.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session expired. Please start a new trial."
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

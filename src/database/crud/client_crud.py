from sqlalchemy.orm import Session
from typing import Optional, List
import secrets
import string
from datetime import datetime

from src.database.models import Client
# APIKey model exists but is not currently used - reserved for future multi-key feature
from src.utils.logger import get_logger

logger = get_logger("client_crud")

def generate_api_key(length: int = 32) -> str:
    """Generate a secure random API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_client(
    db: Session,
    client_id: str,
    name: str,
    email: str,
    company: Optional[str] = None,
    plan_type: str = "free"
) -> Client:
    """Create a new client"""
    
    # Check if client already exists
    existing = db.query(Client).filter(Client.id == client_id).first()
    if existing:
        raise ValueError(f"Client with ID {client_id} already exists")
    
    existing_email = db.query(Client).filter(Client.email == email).first()
    if existing_email:
        raise ValueError(f"Client with email {email} already exists")
    
    # Generate API key
    api_key = generate_api_key()
    
    # Set quota based on plan
    quotas = {
        "free": 1000,      # 1 GB
        "basic": 10000,    # 10 GB
        "premium": 100000  # 100 GB
    }
    
    client = Client(
        id=client_id,
        name=name,
        email=email,
        company=company,
        api_key=api_key,
        plan_type=plan_type,
        monthly_quota_mb=quotas.get(plan_type, 1000)
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    logger.info(f"Created client: {client_id} ({email})")
    return client

def get_client(db: Session, client_id: str) -> Optional[Client]:
    """Get client by ID"""
    return db.query(Client).filter(Client.id == client_id).first()

def get_client_by_email(db: Session, email: str) -> Optional[Client]:
    """Get client by email"""
    return db.query(Client).filter(Client.email == email).first()

def get_client_by_api_key(db: Session, api_key: str) -> Optional[Client]:
    """Get client by API key"""
    return db.query(Client).filter(Client.api_key == api_key).first()

def list_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    """List all clients with pagination"""
    return db.query(Client).offset(skip).limit(limit).all()

def update_client(
    db: Session,
    client_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    company: Optional[str] = None,
    plan_type: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[Client]:
    """Update client details"""
    client = get_client(db, client_id)
    if not client:
        return None
    
    if name:
        client.name = name
    if email:
        client.email = email
    if company:
        client.company = company
    if plan_type:
        client.plan_type = plan_type
        # Update quota based on new plan
        quotas = {"free": 1000, "basic": 10000, "premium": 100000}
        client.monthly_quota_mb = quotas.get(plan_type, 1000)
    if is_active is not None:
        client.is_active = is_active
    
    client.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(client)
    
    logger.info(f"Updated client: {client_id}")
    return client

def delete_client(db: Session, client_id: str) -> bool:
    """Delete a client"""
    client = get_client(db, client_id)
    if not client:
        return False
    
    db.delete(client)
    db.commit()
    
    logger.info(f"Deleted client: {client_id}")
    return True

def update_quota_usage(db: Session, client_id: str, mb_used: float) -> Optional[Client]:
    """Update client's quota usage"""
    client = get_client(db, client_id)
    if not client:
        return None
    
    client.used_quota_mb += mb_used
    db.commit()
    db.refresh(client)
    
    logger.info(f"Updated quota for {client_id}: +{mb_used}MB (total: {client.used_quota_mb}MB)")
    return client

def check_quota(db: Session, client_id: str, required_mb: float) -> bool:
    """Check if client has enough quota"""
    client = get_client(db, client_id)
    if not client:
        return False
    
    available = client.monthly_quota_mb - client.used_quota_mb
    return available >= required_mb

def reset_monthly_quota(db: Session, client_id: str) -> Optional[Client]:
    """Reset client's monthly quota (for billing cycle)"""
    client = get_client(db, client_id)
    if not client:
        return None
    
    client.used_quota_mb = 0.0
    db.commit()
    db.refresh(client)
    
    logger.info(f"Reset quota for client: {client_id}")
    return client
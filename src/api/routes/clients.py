from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from src.api.dependencies import get_db, get_current_client
from src.database.models import Client
from src.database.crud import (
    create_client, get_client, get_client_by_email,
    list_clients, update_client, delete_client,
    get_client_job_count, get_client_completed_jobs,
    get_monthly_usage_summary
)
from src.utils.logger import get_logger

logger = get_logger("clients_api")
router = APIRouter(prefix="/clients", tags=["Client Management"])

class ClientCreate(BaseModel):
    client_id: str = Field(..., description="Unique client identifier")
    name: str = Field(..., description="Client name")
    email: EmailStr = Field(..., description="Client email")
    company: Optional[str] = Field(None, description="Company name")
    plan_type: str = Field("free", description="Subscription plan (free, basic, premium)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "acme_corp",
                "name": "John Doe",
                "email": "john@acme.com",
                "company": "ACME Corporation",
                "plan_type": "basic"
            }
        }

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    plan_type: Optional[str] = None
    is_active: Optional[bool] = None

class ClientResponse(BaseModel):
    id: str
    name: str
    email: str
    company: Optional[str]
    api_key: str
    is_active: bool
    plan_type: str
    monthly_quota_mb: int
    used_quota_mb: float
    created_at: str
    
    class Config:
        orm_mode = True

class ClientDetailResponse(BaseModel):
    id: str
    name: str
    email: str
    company: Optional[str]
    is_active: bool
    plan_type: str
    monthly_quota_mb: int
    used_quota_mb: float
    created_at: str
    total_jobs: int
    completed_jobs: int
    monthly_usage: dict

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_new_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new client account
    
    - **client_id**: Unique identifier for the client
    - **name**: Full name of the client
    - **email**: Email address (must be unique)
    - **company**: Optional company name
    - **plan_type**: Subscription plan (free, basic, premium)
    """
    try:
        client = create_client(
            db=db,
            client_id=client_data.client_id,
            name=client_data.name,
            email=client_data.email,
            company=client_data.company,
            plan_type=client_data.plan_type
        )
        
        return ClientResponse(
            id=client.id,
            name=client.name,
            email=client.email,
            company=client.company,
            api_key=client.api_key,
            is_active=client.is_active,
            plan_type=client.plan_type,
            monthly_quota_mb=client.monthly_quota_mb,
            used_quota_mb=client.used_quota_mb,
            created_at=client.created_at.isoformat()
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me", response_model=ClientDetailResponse)
async def get_current_client_details(
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Get details of the currently authenticated client
    """
    # Get usage stats
    total_jobs = get_client_job_count(db, current_client.id)
    completed_jobs = get_client_completed_jobs(db, current_client.id)
    monthly_usage = get_monthly_usage_summary(db, current_client.id)
    
    return ClientDetailResponse(
        id=current_client.id,
        name=current_client.name,
        email=current_client.email,
        company=current_client.company,
        is_active=current_client.is_active,
        plan_type=current_client.plan_type,
        monthly_quota_mb=current_client.monthly_quota_mb,
        used_quota_mb=current_client.used_quota_mb,
        created_at=current_client.created_at.isoformat(),
        total_jobs=total_jobs,
        completed_jobs=completed_jobs,
        monthly_usage=monthly_usage
    )

@router.get("/{client_id}", response_model=ClientDetailResponse)
async def get_client_details(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a client
    
    - **client_id**: Unique client identifier
    """
    client = get_client(db, client_id)
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    total_jobs = get_client_job_count(db, client_id)
    completed_jobs = get_client_completed_jobs(db, client_id)
    monthly_usage = get_monthly_usage_summary(db, client_id)
    
    return ClientDetailResponse(
        id=client.id,
        name=client.name,
        email=client.email,
        company=client.company,
        is_active=client.is_active,
        plan_type=client.plan_type,
        monthly_quota_mb=client.monthly_quota_mb,
        used_quota_mb=client.used_quota_mb,
        created_at=client.created_at.isoformat(),
        total_jobs=total_jobs,
        completed_jobs=completed_jobs,
        monthly_usage=monthly_usage
    )

@router.get("/", response_model=List[ClientResponse])
async def list_all_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all clients with pagination
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    clients = list_clients(db, skip=skip, limit=limit)
    
    return [
        ClientResponse(
            id=client.id,
            name=client.name,
            email=client.email,
            company=client.company,
            api_key=client.api_key,
            is_active=client.is_active,
            plan_type=client.plan_type,
            monthly_quota_mb=client.monthly_quota_mb,
            used_quota_mb=client.used_quota_mb,
            created_at=client.created_at.isoformat()
        )
        for client in clients
    ]

@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client_details(
    client_id: str,
    update_data: ClientUpdate,
    db: Session = Depends(get_db)
):
    """
    Update client details
    
    - **client_id**: Unique client identifier
    """
    client = update_client(
        db=db,
        client_id=client_id,
        name=update_data.name,
        email=update_data.email,
        company=update_data.company,
        plan_type=update_data.plan_type,
        is_active=update_data.is_active
    )
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return ClientResponse(
        id=client.id,
        name=client.name,
        email=client.email,
        company=client.company,
        api_key=client.api_key,
        is_active=client.is_active,
        plan_type=client.plan_type,
        monthly_quota_mb=client.monthly_quota_mb,
        used_quota_mb=client.used_quota_mb,
        created_at=client.created_at.isoformat()
    )

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_account(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a client account
    
    - **client_id**: Unique client identifier
    
    ⚠️ WARNING: This will also delete all jobs and data associated with this client
    """
    success = delete_client(db, client_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return None

@router.get("/{client_id}/usage", response_model=dict)
async def get_client_usage(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for a client
    
    - **client_id**: Unique client identifier
    """
    client = get_client(db, client_id)
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    usage = get_monthly_usage_summary(db, client_id)
    
    return {
        "client_id": client_id,
        "plan_type": client.plan_type,
        "monthly_quota_mb": client.monthly_quota_mb,
        "used_quota_mb": client.used_quota_mb,
        "remaining_quota_mb": client.monthly_quota_mb - client.used_quota_mb,
        "quota_usage_percent": round((client.used_quota_mb / client.monthly_quota_mb * 100), 2) if client.monthly_quota_mb > 0 else 0,
        "monthly_summary": usage
    }
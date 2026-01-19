from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.core.models import DataType, ProcessingStatus

class JobCreateRequest(BaseModel):
    """Request model for creating a job"""
    client_id: str = Field(..., description="Client identifier")
    data_type: DataType = Field(..., description="Type of data to process")
    config: Optional[Dict[str, Any]] = Field(default={}, description="Processing configuration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "client_123",
                "data_type": "tabular",
                "config": {
                    "remove_duplicates": True,
                    "handle_missing_values": True,
                    "missing_value_strategy": "mean"
                }
            }
        }

class JobResponse(BaseModel):
    """Response model for job information"""
    job_id: str
    client_id: str
    data_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "client_id": "client_123",
                "data_type": "tabular",
                "status": "completed",
                "created_at": "2024-01-15T10:30:00",
                "completed_at": "2024-01-15T10:35:00",
                "output_path": "/data/processed/client_123/file.csv"
            }
        }

class QualityMetricsResponse(BaseModel):
    """Response model for quality metrics"""
    total_records: int
    valid_records: int
    invalid_records: int
    missing_values_percent: float
    duplicate_percent: float
    quality_score: float
    issues: List[str] = []

class JobDetailResponse(BaseModel):
    """Detailed job response including quality metrics"""
    job_id: str
    client_id: str
    data_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    quality_metrics: Optional[QualityMetricsResponse] = None
    error_message: Optional[str] = None

class UploadResponse(BaseModel):
    """Response model for file upload"""
    filename: str
    file_path: str
    file_size: int
    uploaded_at: datetime

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

class DataType(str, Enum):
    """Supported data types"""
    TABULAR = "tabular"
    IMAGE = "image"
    TEXT = "text"
    TIME_SERIES = "time_series"

class ProcessingStatus(str, Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class QualityMetrics(BaseModel):
    """Quality metrics for processed data"""
    total_records: int
    valid_records: int
    invalid_records: int
    missing_values_percent: float
    duplicate_percent: float
    quality_score: float
    issues: List[str] = []
    
    @validator('quality_score')
    def validate_quality_score(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Quality score must be between 0 and 1')
        return v

class ProcessingJob(BaseModel):
    """Processing job model"""
    job_id: str
    client_id: str
    data_type: DataType
    status: ProcessingStatus = ProcessingStatus.PENDING
    input_path: str
    output_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    quality_metrics: Optional[QualityMetrics] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        use_enum_values = True

class ProcessingConfig(BaseModel):
    """Configuration for processing operations"""
    remove_duplicates: bool = True
    handle_missing_values: bool = True
    missing_value_strategy: str = "mean"  # mean, median, mode, drop
    normalize_data: bool = False
    encoding: str = "utf-8"
    # Advanced options
    text_cleaning: bool = True
    remove_html: bool = True
    remove_emojis: bool = True
    collapse_punctuation: bool = True
    normalize_whitespace: bool = True
    enforce_data_types: bool = True
    label_normalization: bool = True
    label_column: Optional[str] = None
    second_duplicate_removal: bool = True
    drop_outliers: bool = False
    outlier_threshold: float = 3.0
    custom_rules: Dict[str, Any] = {}

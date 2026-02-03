from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class DataTypeEnum(enum.Enum):
    """Data type enumeration"""
    TABULAR = "tabular"
    IMAGE = "image"
    TEXT = "text"
    TIME_SERIES = "time_series"

class JobStatusEnum(enum.Enum):
    """Job status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Client(Base):
    """Client/Customer table"""
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    company = Column(String, nullable=True)
    api_key = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    plan_type = Column(String, default="free")  # free, basic, premium, guest
    monthly_quota_mb = Column(Integer, default=1000)  # MB per month
    used_quota_mb = Column(Float, default=0.0)
    expires_at = Column(DateTime, nullable=True)  # For guest accounts
    
    # Relationships
    jobs = relationship("Job", back_populates="client", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client(id={self.id}, name={self.name}, company={self.company})>"

class Job(Base):
    """Job table for tracking preprocessing jobs"""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    
    # Job details
    data_type = Column(Enum(DataTypeEnum), nullable=False)
    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.PENDING)
    
    # Paths
    input_path = Column(String, nullable=False)
    output_path = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    error_message = Column(Text, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Configuration
    config = Column(JSON, nullable=True)
    job_metadata = Column(JSON, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="jobs")
    quality_metrics = relationship("QualityMetric", back_populates="job", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job(id={self.id}, client_id={self.client_id}, status={self.status})>"

class QualityMetric(Base):
    """Quality metrics for processed data"""
    __tablename__ = "quality_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"), unique=True, nullable=False)
    
    # Metrics
    total_records = Column(Integer, nullable=False)
    valid_records = Column(Integer, nullable=False)
    invalid_records = Column(Integer, nullable=False)
    missing_values_percent = Column(Float, default=0.0)
    duplicate_percent = Column(Float, default=0.0)
    quality_score = Column(Float, nullable=False)
    
    # Issues
    issues = Column(JSON, nullable=True)  # List of issues found
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="quality_metrics")
    
    def __repr__(self):
        return f"<QualityMetric(job_id={self.job_id}, quality_score={self.quality_score})>"

class UsageLog(Base):
    """Usage tracking for billing and analytics"""
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=True)
    
    # Usage details
    data_size_mb = Column(Float, nullable=False)
    processing_time_seconds = Column(Float, nullable=False)
    data_type = Column(Enum(DataTypeEnum), nullable=False)
    
    # Cost calculation (for future billing)
    cost_usd = Column(Float, default=0.0)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="usage_logs")
    
    def __repr__(self):
        return f"<UsageLog(client_id={self.client_id}, data_size_mb={self.data_size_mb})>"

class APIKey(Base):
    """
    API Keys for authentication (Future feature)
    
    NOTE: Currently not in use. The system uses Client.api_key directly.
    This model is reserved for future implementation of multiple API keys per client
    with different permissions and rate limits.
    """
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    
    key = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)  # Friendly name for the key
    is_active = Column(Boolean, default=True)
    
    # Permissions
    can_upload = Column(Boolean, default=True)
    can_process = Column(Boolean, default=True)
    can_download = Column(Boolean, default=True)
    
    # Limits
    rate_limit_per_hour = Column(Integer, default=100)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<APIKey(client_id={self.client_id}, name={self.name})>"

class AccessToken(Base):
    __tablename__ = "access_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)

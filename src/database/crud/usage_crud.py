from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.database.models import UsageLog, DataTypeEnum
from src.utils.logger import get_logger

logger = get_logger("usage_crud")

def log_usage(
    db: Session,
    client_id: str,
    job_id: Optional[str],
    data_size_mb: float,
    processing_time_seconds: float,
    data_type: DataTypeEnum,
    cost_usd: float = 0.0
) -> UsageLog:
    """Records the historical log entry for a specific job"""
    usage = UsageLog(
        client_id=client_id,
        job_id=job_id,
        data_size_mb=data_size_mb,
        processing_time_seconds=processing_time_seconds,
        data_type=data_type,
        cost_usd=cost_usd
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    logger.info(f"Logged usage for client {client_id}: {data_size_mb}MB")
    return usage

def get_client_usage(
    db: Session,
    client_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[UsageLog]:
    """Get usage logs for a client with date filter"""
    query = db.query(UsageLog).filter(UsageLog.client_id == client_id)
    
    if start_date:
        query = query.filter(UsageLog.timestamp >= start_date)
    if end_date:
        query = query.filter(UsageLog.timestamp <= end_date)
    
    return query.order_by(UsageLog.timestamp.desc()).all()

def get_monthly_usage_summary(db: Session, client_id: str) -> dict:
    """Aggregates historical logs for the current month"""
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    usage_logs = get_client_usage(db, client_id, start_date=start_of_month)
    
    total_mb = sum(log.data_size_mb for log in usage_logs)
    total_jobs = len(usage_logs)
    total_time = sum(log.processing_time_seconds for log in usage_logs)
    total_cost = sum(log.cost_usd for log in usage_logs)
    
    return {
        'total_data_mb': round(total_mb, 2),
        'total_jobs': total_jobs,
        'total_processing_time_seconds': round(total_time, 2),
        'total_cost_usd': round(total_cost, 2),
        'period_start': start_of_month.isoformat(),
        'period_end': now.isoformat()
    }
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from src.database.models import Job, QualityMetric, DataTypeEnum, JobStatusEnum
from src.core.models import QualityMetrics as QualityMetricsModel
from src.utils.logger import get_logger

logger = get_logger("job_crud")


# =========================
# CREATE JOB
# =========================

def create_job(
    db: Session,
    job_id: str,
    client_id: str,
    data_type: DataTypeEnum,
    input_path: str,
    output_path: Optional[str],
    config: Optional[dict] = None,
    job_metadata: Optional[dict] = None,
) -> Job:
    """Create a new job"""

    job = Job(
        id=job_id,
        client_id=client_id,
        data_type=data_type,
        status=JobStatusEnum.PENDING,
        input_path=input_path,
        output_path=output_path,
        config=config or {},
        job_metadata=job_metadata or {},
        created_at=datetime.utcnow(),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info(f"Created job: {job_id} for client {client_id}")
    return job


# =========================
# GET JOB
# =========================

def get_job(db: Session, job_id: str) -> Optional[Job]:
    """Get job by ID"""
    return db.query(Job).filter(Job.id == job_id).first()


def list_jobs(
    db: Session,
    client_id: Optional[str] = None,
    status: Optional[JobStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Job]:
    """List jobs with optional filters"""

    query = db.query(Job)

    if client_id:
        query = query.filter(Job.client_id == client_id)
    if status:
        query = query.filter(Job.status == status)

    return (
        query.order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# =========================
# UPDATE STATUS
# =========================

def update_job_status(
    db: Session,
    job_id: str,
    status: JobStatusEnum,
    error_message: Optional[str] = None,
) -> Optional[Job]:
    """Update job status"""

    job = get_job(db, job_id)
    if not job:
        return None

    job.status = status

    if status == JobStatusEnum.PROCESSING and not job.started_at:
        job.started_at = datetime.utcnow()

    if status == JobStatusEnum.COMPLETED:
        job.completed_at = datetime.utcnow()
        if job.started_at:
            job.processing_time_seconds = (
                job.completed_at - job.started_at
            ).total_seconds()

    if status == JobStatusEnum.FAILED:
        job.error_message = error_message
        job.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(job)

    logger.info(f"Updated job {job_id} status to {status.value}")
    return job


# =========================
# QUALITY METRICS
# =========================

def add_quality_metrics(
    db: Session,
    job_id: str,
    metrics: QualityMetricsModel,
) -> Optional[QualityMetric]:
    """Add quality metrics to a job"""

    job = get_job(db, job_id)
    if not job:
        return None

    quality_metric = QualityMetric(
        job_id=job_id,
        total_records=metrics.total_records,
        valid_records=metrics.valid_records,
        invalid_records=metrics.invalid_records,
        missing_values_percent=metrics.missing_values_percent,
        duplicate_percent=metrics.duplicate_percent,
        quality_score=metrics.quality_score,
        issues=metrics.issues,
    )

    db.add(quality_metric)
    db.commit()
    db.refresh(quality_metric)

    logger.info(f"Added quality metrics to job {job_id}")
    return quality_metric


# =========================
# GET WITH RELATIONS
# =========================

def get_job_with_metrics(db: Session, job_id: str) -> Optional[Job]:
    """Get job with quality metrics loaded"""
    return db.query(Job).filter(Job.id == job_id).first()


# =========================
# DELETE
# =========================

def delete_job(db: Session, job_id: str) -> bool:
    """Delete a job"""

    job = get_job(db, job_id)
    if not job:
        return False

    db.delete(job)
    db.commit()

    logger.info(f"Deleted job: {job_id}")
    return True


# =========================
# STATS
# =========================

def get_client_job_count(db: Session, client_id: str) -> int:
    """Get total number of jobs for a client"""
    return db.query(Job).filter(Job.client_id == client_id).count()


def get_client_completed_jobs(db: Session, client_id: str) -> int:
    """Get number of completed jobs for a client"""
    return db.query(Job).filter(
        Job.client_id == client_id,
        Job.status == JobStatusEnum.COMPLETED,
    ).count()
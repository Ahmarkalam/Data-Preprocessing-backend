import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from src.core.models import (
    ProcessingJob,
    DataType,
    ProcessingStatus,
    ProcessingConfig,
    QualityMetrics,
)
from src.core.tabular_processor import TabularProcessor
from src.core.image_processor import ImageProcessor
from src.core.text_processor import TextProcessor

from src.database import get_db
from src.database.crud import (
    create_job,
    get_job as get_job_db,
    list_jobs as list_jobs_db,
    update_job_status,
    add_quality_metrics,
    log_usage,
    update_quota_usage,
    check_quota,
)
from src.database.models import DataTypeEnum, JobStatusEnum

from src.utils.logger import get_logger
from config.settings import settings

logger = get_logger("job_manager")


class JobManager:
    """Manages preprocessing jobs with database persistence"""

    def __init__(self):
        self.processors = {
            DataType.TABULAR: TabularProcessor,
            DataType.IMAGE: ImageProcessor,
            DataType.TEXT: TextProcessor,
        }

    # =========================
    # CREATE JOB
    # =========================

    def create_job(
        self,
        client_id: str,
        data_type: DataType,
        input_path: str,
        config: Optional[ProcessingConfig] = None,
        db: Optional[Session] = None,
    ) -> ProcessingJob:

        job_id = str(uuid.uuid4())

        input_file = Path(input_path)
        output_dir = Path(settings.PROCESSED_DATA_DIR) / client_id / job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"processed_{input_file.name}")

        # Normalize data_type to handle both Enum and raw strings
        dt_value = data_type.value if isinstance(data_type, DataType) else str(data_type)
        data_type_enum = DataTypeEnum(dt_value)
        data_type_obj = data_type if isinstance(data_type, DataType) else DataType(dt_value)

        if db is None:
            with get_db() as session:
                create_job(
                    db=session,
                    job_id=job_id,
                    client_id=client_id,
                    data_type=data_type_enum,
                    input_path=input_path,
                    output_path=output_path,
                    config=config.model_dump() if config else {},
                    job_metadata={},
                )
        else:
            create_job(
                db=db,
                job_id=job_id,
                client_id=client_id,
                data_type=data_type_enum,
                input_path=input_path,
                output_path=output_path,
                config=config.model_dump() if config else {},
                job_metadata={},
            )

        logger.info(f"Created job {job_id} for client {client_id}")

        return ProcessingJob(
            job_id=job_id,
            client_id=client_id,
            data_type=data_type_obj,
            status=ProcessingStatus.PENDING,
            input_path=input_path,
            output_path=output_path,
        )

    # =========================
    # EXECUTE JOB
    # =========================

    def execute_job(self, job_id: str, db: Optional[Session] = None) -> ProcessingJob:
        if db is None:
            with get_db() as session:
                return self._execute_job_with_db(job_id, session)
        else:
            return self._execute_job_with_db(job_id, db)

    def _execute_job_with_db(self, job_id: str, db: Session) -> ProcessingJob:
        db_job = get_job_db(db, job_id)
        if not db_job:
            raise ValueError(f"Job {job_id} not found")

        update_job_status(db, job_id, JobStatusEnum.PROCESSING)
        start_time = datetime.utcnow()

        try:
            dt_val = db_job.data_type.value if hasattr(db_job.data_type, "value") else str(db_job.data_type)
            data_type = DataType(dt_val)
            processor_cls = self.processors.get(data_type)

            if not processor_cls:
                raise ValueError(f"No processor for {data_type}")

            config = (
                ProcessingConfig(**db_job.config)
                if db_job.config
                else ProcessingConfig()
            )
            processor = processor_cls(config)

            input_path = Path(db_job.input_path)
            file_size_mb = (
                sum(f.stat().st_size for f in input_path.rglob("*") if f.is_file())
                if input_path.is_dir()
                else input_path.stat().st_size
            ) / (1024 * 1024)

            if not check_quota(db, db_job.client_id, file_size_mb):
                raise Exception("Client quota exceeded")

            if data_type == DataType.TABULAR:
                metrics = processor.process(db_job.input_path, db_job.output_path)
            elif data_type == DataType.IMAGE:
                metrics = processor.process_batch(db_job.input_path, db_job.output_path)
            elif data_type == DataType.TEXT:
                metrics = processor.process(db_job.input_path, db_job.output_path)
            else:
                raise ValueError("Unsupported data type")

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            update_job_status(db, job_id, JobStatusEnum.COMPLETED)
            add_quality_metrics(db, job_id, metrics)

            log_usage(
                db=db,
                client_id=db_job.client_id,
                job_id=job_id,
                data_size_mb=file_size_mb,
                processing_time_seconds=processing_time,
                data_type=db_job.data_type,
            )

            update_quota_usage(db, db_job.client_id, file_size_mb)

            logger.info(f"Job {job_id} completed successfully")

            return ProcessingJob(
                job_id=job_id,
                client_id=db_job.client_id,
                data_type=data_type,
                status=ProcessingStatus.COMPLETED,
                input_path=db_job.input_path,
                output_path=db_job.output_path,
                created_at=db_job.created_at,
                completed_at=datetime.utcnow(),
                quality_metrics=metrics,
            )

        except Exception as e:
            update_job_status(
                db,
                job_id,
                JobStatusEnum.FAILED,
                error_message=str(e),
            )
            logger.exception(f"Job {job_id} failed")
            raise

    # =========================
    # GET JOB
    # =========================

    def get_job(self, job_id: str, db: Optional[Session] = None) -> Optional[ProcessingJob]:
        """Get job by ID"""
        if db is None:
            with get_db() as session:
                return self._get_job_with_db(job_id, session)
        else:
            return self._get_job_with_db(job_id, db)

    def _get_job_with_db(self, job_id: str, db: Session) -> Optional[ProcessingJob]:
        """Internal method to get job with database session"""
        db_job = get_job_db(db, job_id)
        if not db_job:
            return None

        # Convert database model to ProcessingJob
        dt_val = db_job.data_type.value if hasattr(db_job.data_type, "value") else str(db_job.data_type)
        st_val = db_job.status.value if hasattr(db_job.status, "value") else str(db_job.status)
        data_type = DataType(dt_val)
        status = ProcessingStatus(st_val)

        quality_metrics = None
        if db_job.quality_metrics:
            quality_metrics = QualityMetrics(
                total_records=db_job.quality_metrics.total_records,
                valid_records=db_job.quality_metrics.valid_records,
                invalid_records=db_job.quality_metrics.invalid_records,
                missing_values_percent=db_job.quality_metrics.missing_values_percent,
                duplicate_percent=db_job.quality_metrics.duplicate_percent,
                quality_score=db_job.quality_metrics.quality_score,
                issues=db_job.quality_metrics.issues or [],
            )

        return ProcessingJob(
            job_id=db_job.id,
            client_id=db_job.client_id,
            data_type=data_type,
            status=status,
            input_path=db_job.input_path,
            output_path=db_job.output_path,
            created_at=db_job.created_at,
            completed_at=db_job.completed_at,
            error_message=db_job.error_message,
            quality_metrics=quality_metrics,
            metadata=db_job.job_metadata or {},
        )

    # =========================
    # LIST JOBS
    # =========================

    def list_jobs(
        self,
        client_id: Optional[str] = None,
        status: Optional[ProcessingStatus] = None,
        skip: int = 0,
        limit: int = 100,
        db: Optional[Session] = None,
    ) -> list[ProcessingJob]:
        """List jobs with optional filters"""
        if db is None:
            with get_db() as session:
                return self._list_jobs_with_db(client_id, status, skip, limit, session)
        else:
            return self._list_jobs_with_db(client_id, status, skip, limit, db)

    def _list_jobs_with_db(
        self,
        client_id: Optional[str],
        status: Optional[ProcessingStatus],
        skip: int,
        limit: int,
        db: Session,
    ) -> list[ProcessingJob]:
        """Internal method to list jobs with database session"""
        status_enum = None
        if status:
            status_enum = JobStatusEnum(status.value)

        db_jobs = list_jobs_db(
            db=db,
            client_id=client_id,
            status=status_enum,
            skip=skip,
            limit=limit,
        )

        jobs = []
        for db_job in db_jobs:
            dt_val = db_job.data_type.value if hasattr(db_job.data_type, "value") else str(db_job.data_type)
            st_val = db_job.status.value if hasattr(db_job.status, "value") else str(db_job.status)
            data_type = DataType(dt_val)
            job_status = ProcessingStatus(st_val)

            quality_metrics = None
            if db_job.quality_metrics:
                quality_metrics = QualityMetrics(
                    total_records=db_job.quality_metrics.total_records,
                    valid_records=db_job.quality_metrics.valid_records,
                    invalid_records=db_job.quality_metrics.invalid_records,
                    missing_values_percent=db_job.quality_metrics.missing_values_percent,
                    duplicate_percent=db_job.quality_metrics.duplicate_percent,
                    quality_score=db_job.quality_metrics.quality_score,
                    issues=db_job.quality_metrics.issues or [],
                )

            jobs.append(
                ProcessingJob(
                    job_id=db_job.id,
                    client_id=db_job.client_id,
                    data_type=data_type,
                    status=job_status,
                    input_path=db_job.input_path,
                    output_path=db_job.output_path,
                    created_at=db_job.created_at,
                    completed_at=db_job.completed_at,
                    error_message=db_job.error_message,
                    quality_metrics=quality_metrics,
                    config=db_job.config or {},
                    metadata=db_job.job_metadata or {},
                )
            )

        return jobs

    # =========================
    # GET JOB STATUS
    # =========================

    def get_job_status(self, job_id: str, db: Optional[Session] = None) -> dict:
        """Get job status as dictionary"""
        job = self.get_job(job_id, db)
        if not job:
            return {"error": "Job not found"}

        st = job.status.value if hasattr(job.status, "value") else str(job.status)
        return {
            "job_id": job.job_id,
            "status": st,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": None,  # Could be added to ProcessingJob model
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
            "quality_score": job.quality_metrics.quality_score if job.quality_metrics else None,
        }

    # =========================
    # CANCEL JOB
    # =========================

    def cancel_job(self, job_id: str, db: Optional[Session] = None) -> bool:
        """Cancel a pending job"""
        if db is None:
            with get_db() as session:
                return self._cancel_job_with_db(job_id, session)
        else:
            return self._cancel_job_with_db(job_id, db)

    def _cancel_job_with_db(self, job_id: str, db: Session) -> bool:
        """Internal method to cancel job with database session"""
        db_job = get_job_db(db, job_id)
        if not db_job:
            return False

        # Only allow cancellation of pending jobs
        if db_job.status != JobStatusEnum.PENDING:
            logger.warning(f"Cannot cancel job {job_id} - status is {db_job.status.value}")
            return False

        update_job_status(
            db,
            job_id,
            JobStatusEnum.FAILED,
            error_message="Job cancelled by user",
        )
        logger.info(f"Cancelled job {job_id}")
        return True

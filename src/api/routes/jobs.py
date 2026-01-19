from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from typing import List, Optional
from pathlib import Path
from sqlalchemy.orm import Session

from src.api.schemas import (
    JobCreateRequest, JobResponse, JobDetailResponse, 
    QualityMetricsResponse
)
from src.api.dependencies import get_db, get_current_client, get_optional_client
from src.pipelines.job_manager import JobManager
from src.core.models import ProcessingConfig, DataType
from src.database.models import Client
from src.database.crud import check_quota
from src.utils.logger import get_logger

logger = get_logger("jobs_api")
router = APIRouter(prefix="/jobs", tags=["Job Processing"])

job_manager = JobManager()

def process_job_in_background(job_id: str):
    """Background task to process a job"""
    try:
        job_manager.execute_job(job_id)
        logger.info(f"Background processing completed for job {job_id}")
    except Exception as e:
        logger.error(f"Background processing failed for job {job_id}: {e}")

@router.post("/create", response_model=JobResponse)
async def create_job(
    data_type: DataType = Query(..., description="Data type"),
    input_path: str = Query(..., description="Path to input file/directory"),
    background_tasks: BackgroundTasks = None,
    remove_duplicates: bool = Query(True, description="Remove duplicate records"),
    handle_missing_values: bool = Query(True, description="Handle missing values"),
    missing_value_strategy: str = Query("mean", description="Strategy for missing values"),
    normalize_data: bool = Query(False, description="Normalize numeric data"),
    auto_execute: bool = Query(True, description="Automatically execute the job"),
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Create a new preprocessing job (Requires Authentication)
    
    **Authentication**: Include your API key in the `X-API-Key` header
    
    - **data_type**: Type of data (tabular, image, text)
    - **input_path**: Full path to the input file or directory
    - **auto_execute**: If true, job starts processing immediately
    """
    try:
        if not Path(input_path).exists():
            raise HTTPException(status_code=404, detail="Input file/directory not found")
        
       
        input_path_obj = Path(input_path)
        if input_path_obj.is_file():
            file_size_mb = input_path_obj.stat().st_size / (1024 * 1024)
        else:
            file_size_mb = sum(f.stat().st_size for f in input_path_obj.rglob('*') if f.is_file()) / (1024 * 1024)
        
        
        if not check_quota(db, client.id, file_size_mb):
            raise HTTPException(
                status_code=403,
                detail=f"Quota exceeded. File size: {file_size_mb:.2f}MB, Available: {client.monthly_quota_mb - client.used_quota_mb:.2f}MB"
            )
        
        config = ProcessingConfig(
            remove_duplicates=remove_duplicates,
            handle_missing_values=handle_missing_values,
            missing_value_strategy=missing_value_strategy,
            normalize_data=normalize_data
        )
        
        job = job_manager.create_job(
            client_id=client.id,
            data_type=data_type,
            input_path=input_path,
            config=config,
            db=db
        )
        
        
        if auto_execute and background_tasks:
            background_tasks.add_task(process_job_in_background, job.job_id)
            logger.info(f"Job {job.job_id} queued for background processing")
        
        return JobResponse(
            job_id=job.job_id,
            client_id=job.client_id,
            data_type=job.data_type.value,
            status=job.status.value,
            created_at=job.created_at,
            completed_at=job.completed_at,
            output_path=job.output_path
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{job_id}/execute", response_model=JobDetailResponse)
async def execute_job(
    job_id: str,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Execute a job synchronously (Requires Authentication)
    
    **Authentication**: Include your API key in the `X-API-Key` header
    
    - **job_id**: Unique job identifier
    """
    try:
        job = job_manager.get_job(job_id, db)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied to this job")
        
        job = job_manager.execute_job(job_id, db)
        
        quality_metrics = None
        if job.quality_metrics:
            quality_metrics = QualityMetricsResponse(**job.quality_metrics.dict())
        
        return JobDetailResponse(
            job_id=job.job_id,
            client_id=job.client_id,
            data_type=job.data_type.value,
            status=job.status.value,
            created_at=job.created_at,
            completed_at=job.completed_at,
            quality_metrics=quality_metrics,
            error_message=job.error_message
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: str,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Get job details by ID (Requires Authentication)
    
    **Authentication**: Include your API key in the `X-API-Key` header
    
    - **job_id**: Unique job identifier
    """
    try:
        job = job_manager.get_job(job_id, db)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied to this job")
        
        quality_metrics = None
        if job.quality_metrics:
            quality_metrics = QualityMetricsResponse(**job.quality_metrics.dict())
        
        return JobDetailResponse(
            job_id=job.job_id,
            client_id=job.client_id,
            data_type=job.data_type.value,
            status=job.status.value,
            created_at=job.created_at,
            completed_at=job.completed_at,
            quality_metrics=quality_metrics,
            error_message=job.error_message
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of jobs to return"),
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    List your jobs (Requires Authentication)
    
    **Authentication**: Include your API key in the `X-API-Key` header
    
    - **limit**: Maximum number of results
    """
    try:
        jobs = job_manager.list_jobs(client_id=client.id, db=db)
        
        jobs = jobs[:limit]
        
        return [
            JobResponse(
                job_id=job.job_id,
                client_id=job.client_id,
                data_type=job.data_type.value,
                status=job.status.value,
                created_at=job.created_at,
                completed_at=job.completed_at,
                output_path=job.output_path,
                error_message=job.error_message
            )
            for job in jobs
        ]
    
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}/status")
async def get_job_status(
    job_id: str,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Get current job status (Requires Authentication)
    
    **Authentication**: Include your API key in the `X-API-Key` header
    
    - **job_id**: Unique job identifier
    """
    try:
        job = job_manager.get_job(job_id, db)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied to this job")
        
        status = job_manager.get_job_status(job_id, db)
        
        if 'error' in status:
            raise HTTPException(status_code=404, detail=status['error'])
        
        return status
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{job_id}/cancel", response_model=JobDetailResponse)
async def cancel_job(
    job_id: str,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Cancel a pending job (Requires Authentication)
    
    **Authentication**: Include your API key in the `X-API-Key` header
    
    - **job_id**: Unique job identifier
    """
    try:
        job = job_manager.get_job(job_id, db)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Verify job belongs to client
        if job.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied to this job")
        
        # Cancel the job
        success = job_manager.cancel_job(job_id, db)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Job cannot be cancelled. Only pending jobs can be cancelled."
            )
        
        # Get updated job
        job = job_manager.get_job(job_id, db)
        
        quality_metrics = None
        if job and job.quality_metrics:
            quality_metrics = QualityMetricsResponse(**job.quality_metrics.dict())
        
        return JobDetailResponse(
            job_id=job.job_id,
            client_id=job.client_id,
            data_type=job.data_type.value,
            status=job.status.value,
            created_at=job.created_at,
            completed_at=job.completed_at,
            quality_metrics=quality_metrics,
            error_message=job.error_message
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}/download")
async def download_processed_file(
    job_id: str,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Download processed file (Requires Authentication)
    
    **Authentication**: Include your API key in the `X-API-Key` header
    
    - **job_id**: Unique job identifier
    """
    try:
        job = job_manager.get_job(job_id, db)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied to this job")
        
        if job.status.value != "completed":
            raise HTTPException(status_code=400, detail="Job not completed yet")
        
        if not job.output_path:
            raise HTTPException(status_code=404, detail="Output file not found")
        
        output_path = Path(job.output_path)
        
        if not output_path.exists():
            raise HTTPException(status_code=404, detail="Output file does not exist")
        
        from fastapi.responses import FileResponse
        
        return FileResponse(
            path=str(output_path),
            filename=output_path.name,
            media_type='application/octet-stream'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
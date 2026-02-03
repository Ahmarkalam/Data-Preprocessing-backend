from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
import io
from pathlib import Path
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

from src.api.schemas import (
    JobCreateRequest, JobResponse, JobDetailResponse, 
    QualityMetricsResponse
)
from src.api.dependencies import get_db, get_current_client, get_optional_client
from src.pipelines.job_manager import JobManager
from src.core.models import ProcessingConfig, DataType
from src.core.analyzer import DatasetAnalyzer
from src.core.chat import DataChatEngine
from src.database.models import Client
from src.database.crud import check_quota
from src.utils.logger import get_logger

logger = get_logger("jobs_api")
router = APIRouter(prefix="/jobs", tags=["Job Processing"])

job_manager = JobManager()

@router.post("/analyze")
async def analyze_dataset(
    input_path: str = Query(..., description="Path to input file/directory"),
    client: Client = Depends(get_current_client),
):
    """
    Analyze dataset and provide preprocessing suggestions (Requires Authentication)
    """
    try:
        if not Path(input_path).exists():
            raise HTTPException(status_code=404, detail="Input file not found")

        # Load data (limit to first 1000 rows for analysis)
        file_ext = Path(input_path).suffix.lower()
        df = None
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(input_path, nrows=1000)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(input_path, nrows=1000)
            elif file_ext == '.json':
                df = pd.read_json(input_path)
                if len(df) > 1000:
                    df = df.head(1000)
            elif file_ext == '.parquet':
                df = pd.read_parquet(input_path)
                if len(df) > 1000:
                    df = df.head(1000)
        except Exception as e:
            logger.error(f"Error reading file for analysis: {e}")
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
        
        if df is None:
             raise HTTPException(status_code=400, detail="Unsupported file format")

        analyzer = DatasetAnalyzer()
        results = analyzer.analyze(df)
        
        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{job_id}/chat")
async def chat_with_data(
    job_id: str,
    query: str = Query(..., description="User query"),
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Chat with your dataset (Requires Authentication)
    """
    try:
        job = job_manager.get_job(job_id, db)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Load data (cached or read)
        # Prefer output path if exists, else input path
        target_path = job.output_path if (job.output_path and Path(job.output_path).exists()) else job.input_path
        
        if not target_path or not Path(target_path).exists():
             return {"response": "Data file not available for chat."}

        # Read df
        file_ext = Path(target_path).suffix.lower()
        df = None
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(target_path, nrows=5000)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(target_path, nrows=5000)
            elif file_ext == '.json':
                df = pd.read_json(target_path)
                if len(df) > 5000:
                    df = df.head(5000)
            elif file_ext == '.parquet':
                df = pd.read_parquet(target_path)
                if len(df) > 5000:
                    df = df.head(5000)
        except Exception:
             return {"response": "Could not read data file for analysis."}
        
        if df is None:
             return {"response": "Unsupported file format for chat."}

        chat_engine = DataChatEngine()
        response = chat_engine.process_query(query, df, job)
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    # Advanced options
    text_cleaning: bool = Query(True, description="Clean text columns"),
    remove_html: bool = Query(True, description="Strip HTML tags from text"),
    remove_emojis: bool = Query(True, description="Remove emojis from text"),
    collapse_punctuation: bool = Query(True, description="Collapse repeated punctuation"),
    normalize_whitespace: bool = Query(True, description="Normalize whitespace"),
    enforce_data_types: bool = Query(True, description="Coerce numeric types and treat empty strings as missing"),
    label_normalization: bool = Query(True, description="Normalize label column to 0/1"),
    label_column: Optional[str] = Query(None, description="Explicit label column name"),
    second_duplicate_removal: bool = Query(True, description="Remove duplicates after cleaning"),
    drop_outliers: bool = Query(False, description="Drop outlier rows by z-score"),
    outlier_threshold: float = Query(3.0, description="Z-score threshold for outliers"),
    # New options
    parse_dates: bool = Query(False, description="Auto-detect and parse date columns"),
    encoding_strategy: str = Query("none", description="Categorical encoding strategy (none, onehot, label)"),
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
            normalize_data=normalize_data,
            text_cleaning=text_cleaning,
            remove_html=remove_html,
            remove_emojis=remove_emojis,
            collapse_punctuation=collapse_punctuation,
            normalize_whitespace=normalize_whitespace,
            enforce_data_types=enforce_data_types,
            label_normalization=label_normalization,
            label_column=label_column,
            second_duplicate_removal=second_duplicate_removal,
            drop_outliers=drop_outliers,
            outlier_threshold=outlier_threshold
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
        
        dt = job.data_type.value if hasattr(job.data_type, "value") else job.data_type
        st = job.status.value if hasattr(job.status, "value") else job.status
        return JobResponse(
            job_id=job.job_id,
            client_id=job.client_id,
            data_type=dt,
            status=st,
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
        
        dt = job.data_type.value if hasattr(job.data_type, "value") else job.data_type
        st = job.status.value if hasattr(job.status, "value") else job.status
        return JobDetailResponse(
            job_id=job.job_id,
            client_id=job.client_id,
            data_type=dt,
            status=st,
            created_at=job.created_at,
            completed_at=job.completed_at,
            quality_metrics=quality_metrics,
            error_message=job.error_message,
            config=job.config
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}/preview")
async def get_job_preview(
    job_id: str,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Get job preview data (Requires Authentication)
    """
    try:
        job = job_manager.get_job(job_id, db)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied to this job")
        
        preview_data = {"original": [], "cleaned": [], "summary": {}}
        df_orig = None
        df_clean = None
        
        # Read Original Data (limit 50)
        try:
            if job.input_path and Path(job.input_path).exists():
                file_ext = Path(job.input_path).suffix.lower()
                if file_ext == '.csv':
                    df_orig = pd.read_csv(job.input_path, nrows=50)
                elif file_ext in ['.xlsx', '.xls']:
                    df_orig = pd.read_excel(job.input_path, nrows=50)
                elif file_ext == '.json':
                    df_orig = pd.read_json(job.input_path)
                    df_orig = df_orig.head(50)
                elif file_ext == '.parquet':
                    df_orig = pd.read_parquet(job.input_path)
                    df_orig = df_orig.head(50)
                else:
                    df_orig = pd.DataFrame()
                
                df_orig = df_orig.replace({np.nan: None})
                preview_data["original"] = df_orig.to_dict(orient='records')
        except Exception as e:
            logger.error(f"Error reading original file: {e}")

        # Read Cleaned Data (limit 50)
        try:
            if job.output_path and Path(job.output_path).exists():
                file_ext = Path(job.output_path).suffix.lower()
                if file_ext == '.csv':
                    df_clean = pd.read_csv(job.output_path, nrows=50)
                elif file_ext in ['.xlsx', '.xls']:
                    df_clean = pd.read_excel(job.output_path, nrows=50)
                elif file_ext == '.json':
                    df_clean = pd.read_json(job.output_path)
                    df_clean = df_clean.head(50)
                elif file_ext == '.parquet':
                    df_clean = pd.read_parquet(job.output_path)
                    df_clean = df_clean.head(50)
                else:
                    df_clean = pd.DataFrame()
                
                df_clean = df_clean.replace({np.nan: None})
                preview_data["cleaned"] = df_clean.to_dict(orient='records')
        except Exception as e:
            logger.error(f"Error reading cleaned file: {e}")
        
        try:
            analyzer = DatasetAnalyzer()
            summary = {}
            if isinstance(df_orig, pd.DataFrame) and len(df_orig.columns) > 0:
                df_o = df_orig.replace({None: np.nan})
                summary["original"] = analyzer.analyze(df_o)
            if isinstance(df_clean, pd.DataFrame) and len(df_clean.columns) > 0:
                df_c = df_clean.replace({None: np.nan})
                summary["cleaned"] = analyzer.analyze(df_c)
            if summary:
                try:
                    o_rows = summary.get("original", {}).get("total_rows")
                    c_rows = summary.get("cleaned", {}).get("total_rows")
                    if isinstance(o_rows, int) and isinstance(c_rows, int):
                        summary["diff"] = {"rows_delta": o_rows - c_rows}
                except Exception:
                    pass
                preview_data["summary"] = summary
        except Exception as e:
            logger.error(f"Error generating preview summary: {e}")
        
        return preview_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job preview {job_id}: {e}")
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
                data_type=(job.data_type.value if hasattr(job.data_type, "value") else job.data_type),
                status=(job.status.value if hasattr(job.status, "value") else job.status),
                created_at=job.created_at,
                completed_at=job.completed_at,
                output_path=job.output_path,
                error_message=job.error_message,
                config=job.config
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
        
        dt = job.data_type.value if hasattr(job.data_type, "value") else job.data_type
        st = job.status.value if hasattr(job.status, "value") else job.status
        return JobDetailResponse(
            job_id=job.job_id,
            client_id=job.client_id,
            data_type=dt,
            status=st,
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
        
        st = job.status.value if hasattr(job.status, "value") else str(job.status)
        if st != "completed":
            raise HTTPException(status_code=400, detail="Job not completed yet")
        
        if not job.output_path:
            raise HTTPException(status_code=404, detail="Output file not found")
        
        output_path = Path(job.output_path)
        
        if not output_path.exists():
            raise HTTPException(status_code=404, detail="Output file does not exist")
        
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

@router.get("/{job_id}/report")
async def get_job_report(
    job_id: str,
    format: str = Query("json", regex="^(json|pdf)$"),
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Get job quality report in JSON or PDF format (Requires Authentication)
    """
    try:
        job = job_manager.get_job(job_id, db)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied to this job")
            
        st = job.status.value if hasattr(job.status, "value") else str(job.status)
        if st != "completed":
            raise HTTPException(status_code=400, detail="Job not completed yet")
            
        if not job.quality_metrics:
            raise HTTPException(status_code=404, detail="No quality metrics available")

        if format == "json":
            return job.quality_metrics.dict()
        
        elif format == "pdf":
            generator = ReportGenerator()
            pdf_bytes = generator.generate_pdf(job)
            
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=report_{job_id}.pdf"}
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import shutil
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from src.api.schemas import UploadResponse
from src.api.dependencies import get_db, get_current_client
from src.database.models import Client
from src.database.crud import check_quota  
from src.utils.logger import get_logger
from config.settings import settings

logger = get_logger("upload_api")
router = APIRouter(prefix="/upload", tags=["File Upload"])



def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def sanitize_filename(filename: str) -> str:
    return Path(filename).name.replace(" ", "_")


def validate_file_size_mb(size_mb: float, max_mb: int = 500):
    if size_mb > max_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max allowed {max_mb}MB"
        )



@router.post("/tabular", response_model=UploadResponse)
async def upload_tabular_file(
    file: UploadFile = File(...),
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    ext = get_file_extension(file.filename)
    if ext not in settings.SUPPORTED_TABULAR_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {settings.SUPPORTED_TABULAR_FORMATS}"
        )

    client_dir = Path(settings.RAW_DATA_DIR) / client.id / "tabular"
    client_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = sanitize_filename(file.filename)
    file_path = client_dir / f"{timestamp}_{safe_name}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    validate_file_size_mb(file_size_mb)

    if not check_quota(db, client.id, file_size_mb):
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=403, detail="Quota exceeded")

    logger.info(f"Tabular uploaded: {file_path}")

    return UploadResponse(
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_path.stat().st_size,
        uploaded_at=datetime.utcnow()
    )



@router.post("/images", response_model=List[UploadResponse])
async def upload_image_files(
    files: List[UploadFile] = File(...),
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    client_dir = Path(settings.RAW_DATA_DIR) / client.id / "images"
    client_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files: List[UploadResponse] = []
    total_size_mb = 0.0

    for file in files:
        ext = get_file_extension(file.filename)
        if ext not in settings.SUPPORTED_IMAGE_FORMATS:
            continue

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = sanitize_filename(file.filename)
        file_path = client_dir / f"{timestamp}_{safe_name}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        size_mb = file_path.stat().st_size / (1024 * 1024)
        total_size_mb += size_mb

        uploaded_files.append(
            UploadResponse(
                filename=file.filename,
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                uploaded_at=datetime.utcnow()
            )
        )

        logger.info(f"Image uploaded: {file_path}")

    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No valid image files")

    if not check_quota(db, client.id, total_size_mb):
        for f in uploaded_files:
            Path(f.file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=403, detail="Quota exceeded")

    return uploaded_files



@router.post("/text", response_model=UploadResponse)
async def upload_text_file(
    file: UploadFile = File(...),
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    ext = get_file_extension(file.filename)
    if ext not in settings.SUPPORTED_TEXT_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {settings.SUPPORTED_TEXT_FORMATS}"
        )

    client_dir = Path(settings.RAW_DATA_DIR) / client.id / "text"
    client_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = sanitize_filename(file.filename)
    file_path = client_dir / f"{timestamp}_{safe_name}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    validate_file_size_mb(file_size_mb)

    if not check_quota(db, client.id, file_size_mb):
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=403, detail="Quota exceeded")

    logger.info(f"Text uploaded: {file_path}")

    return UploadResponse(
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_path.stat().st_size,
        uploaded_at=datetime.utcnow()
    )

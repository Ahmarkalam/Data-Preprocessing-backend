import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Central configuration for the preprocessing backend"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    TEMP_DIR = DATA_DIR / "temp"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Processing settings
    MAX_FILE_SIZE_MB = 500
    CHUNK_SIZE = 10000  # For processing large files in chunks
    MAX_WORKERS = 4  # For parallel processing
    
    # Supported formats
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    SUPPORTED_TABULAR_FORMATS = ['.csv', '.xlsx', '.xls', '.json', '.parquet']
    SUPPORTED_TEXT_FORMATS = ['.txt', '.doc', '.docx', '.pdf']
    
    # Quality thresholds
    MIN_DATA_QUALITY_SCORE = 0.85
    MAX_MISSING_VALUES_PERCENT = 10
    MAX_DUPLICATE_PERCENT = 5
    
    # Cloud storage (AWS S3)
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', 'data-preprocessing-bucket')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./preprocessing.db')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Auth/session
    SESSION_SECRET = os.getenv('SESSION_SECRET', 'dev-change-me')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    @classmethod
    def create_directories(cls):
        """Create all necessary directories"""
        for dir_path in [cls.RAW_DATA_DIR, cls.PROCESSED_DATA_DIR, 
                         cls.TEMP_DIR, cls.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return {
            'max_file_size_mb': cls.MAX_FILE_SIZE_MB,
            'chunk_size': cls.CHUNK_SIZE,
            'max_workers': cls.MAX_WORKERS,
            'min_quality_score': cls.MIN_DATA_QUALITY_SCORE
        }

settings = Settings()
settings.create_directories()

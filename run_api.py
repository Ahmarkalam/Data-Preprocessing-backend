#!/usr/bin/env python
"""
Script to run the Data Preprocessing API
"""
import uvicorn
from src.utils.logger import get_logger

logger = get_logger("startup")

if __name__ == "__main__":
    logger.info("Starting Data Preprocessing API server...")
    logger.info("API will be available at: http://localhost:8000")
    logger.info("API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",  # Changed from 0.0.0.0 to 127.0.0.1
        port=8000,
        reload=True,
        log_level="info"
    )
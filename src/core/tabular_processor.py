import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
from src.utils.logger import get_logger
from src.core.models import QualityMetrics, ProcessingConfig

logger = get_logger("tabular_processor")

class TabularProcessor:
    """Handles all tabular data preprocessing"""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load data from various formats"""
        path = Path(file_path)
        
        try:
            if path.suffix == '.csv':
                df = pd.read_csv(file_path, encoding=self.config.encoding)
            elif path.suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif path.suffix == '.json':
                df = pd.read_json(file_path)
            elif path.suffix == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
            
            logger.info(f"Loaded data from {file_path}: {df.shape}")
            return df
        
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            raise
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names"""
        df.columns = (df.columns
                      .str.strip()
                      .str.lower()
                      .str.replace(' ', '_')
                      .str.replace('[^a-zA-Z0-9_]', '', regex=True))
        logger.info("Cleaned column names")
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values based on strategy"""
        strategy = self.config.missing_value_strategy
        
        initial_missing = df.isnull().sum().sum()
        
        if strategy == "drop":
            df = df.dropna()
        elif strategy == "mean":
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        elif strategy == "median":
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        elif strategy == "mode":
            for col in df.columns:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else None)
        
        final_missing = df.isnull().sum().sum()
        logger.info(f"Handled missing values: {initial_missing} -> {final_missing}")
        
        return df
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows"""
        initial_count = len(df)
        df = df.drop_duplicates()
        removed_count = initial_count - len(df)
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate rows")
        
        return df
    
    def detect_outliers(self, df: pd.DataFrame, threshold: float = 3.0) -> Dict[str, List[int]]:
        """Detect outliers using Z-score method"""
        outliers = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outlier_indices = df[z_scores > threshold].index.tolist()
            
            if outlier_indices:
                outliers[col] = outlier_indices
        
        logger.info(f"Detected outliers in {len(outliers)} columns")
        return outliers
    
    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize numeric columns to 0-1 range"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            min_val = df[col].min()
            max_val = df[col].max()
            
            if max_val > min_val:
                df[col] = (df[col] - min_val) / (max_val - min_val)
        
        logger.info(f"Normalized {len(numeric_cols)} numeric columns")
        return df
    
    def calculate_quality_metrics(self, df: pd.DataFrame, 
                                  original_count: int) -> QualityMetrics:
        """Calculate quality metrics for the processed data"""
        total_records = len(df)
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        missing_percent = (missing_cells / total_cells * 100) if total_cells > 0 else 0
        
        # Calculate duplicate percentage based on original data
        duplicate_percent = ((original_count - total_records) / original_count * 100) if original_count > 0 else 0
        
        # Calculate quality score (simple heuristic)
        quality_score = max(0, 1 - (missing_percent / 100) - (duplicate_percent / 200))
        
        issues = []
        if missing_percent > 10:
            issues.append(f"High missing values: {missing_percent:.2f}%")
        if duplicate_percent > 5:
            issues.append(f"High duplicates: {duplicate_percent:.2f}%")
        
        # Handle division by zero - check if dataframe has columns
        num_columns = len(df.columns) if len(df.columns) > 0 else 1
        invalid_records = int(missing_cells / num_columns) if num_columns > 0 else 0
        
        return QualityMetrics(
            total_records=total_records,
            valid_records=max(0, total_records - invalid_records),
            invalid_records=invalid_records,
            missing_values_percent=round(missing_percent, 2),
            duplicate_percent=round(duplicate_percent, 2),
            quality_score=round(quality_score, 3),
            issues=issues
        )
    
    def process(self, input_path: str, output_path: str) -> QualityMetrics:
        """Main processing pipeline"""
        logger.info(f"Starting tabular data processing: {input_path}")
        
        # Load data
        df = self.load_data(input_path)
        original_count = len(df)
        
        # Clean column names
        df = self.clean_column_names(df)
        
        # Remove duplicates
        if self.config.remove_duplicates:
            df = self.remove_duplicates(df)
        
        # Handle missing values
        if self.config.handle_missing_values:
            df = self.handle_missing_values(df)
        
        # Normalize if requested
        if self.config.normalize_data:
            df = self.normalize_data(df)
        
        # Save processed data
        output_path_obj = Path(output_path)
        if output_path_obj.suffix == '.csv':
            df.to_csv(output_path, index=False)
        elif output_path_obj.suffix in ['.xlsx', '.xls']:
            df.to_excel(output_path, index=False)
        elif output_path_obj.suffix == '.parquet':
            df.to_parquet(output_path, index=False)
        
        logger.info(f"Saved processed data to: {output_path}")
        
        # Calculate and return quality metrics
        metrics = self.calculate_quality_metrics(df, original_count)
        logger.info(f"Quality score: {metrics.quality_score}")
        
        return metrics
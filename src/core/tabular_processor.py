import pandas as pd
import numpy as np
import re
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
        df.columns = (df.columns.astype(str)
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
    
    def _clean_text_value(self, s: Any) -> Any:
        if pd.isna(s):
            return s
        s = str(s)
        s = s.strip().lower()
        if self.config.remove_html:
            s = re.sub(r'<[^>]+>', '', s)
        if self.config.remove_emojis:
            s = re.sub(r'[\U00010000-\U0010ffff]', '', s)
        if self.config.collapse_punctuation:
            s = re.sub(r'([.!?;,:\-])\1+', r'\1', s)
        if self.config.normalize_whitespace:
            s = ' '.join(s.split())
        if s in {"", "null", "none", "nan"}:
            return np.nan
        return s
    
    def clean_text_columns(self, df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
        """Clean text in object columns and count changes"""
        changed = 0
        cleaned_cols = 0
        obj_cols = df.select_dtypes(include=['object']).columns
        for col in obj_cols:
            before = df[col].astype(str)
            df[col] = df[col].apply(self._clean_text_value)
            cleaned_cols += 1
            after = df[col].astype(str)
            changed += (before != after).sum()
        return df, cleaned_cols, changed
    
    def enforce_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Coerce numeric columns and treat empty strings as NaN"""
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].replace({"": np.nan})
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    
    def _detect_label_column(self, df: pd.DataFrame) -> Optional[str]:
        candidates = ["label", "target", "y", "class"]
        label = self.config.label_column or None
        if label and label in df.columns:
            return label
        for c in candidates:
            if c in df.columns:
                return c
        return None
    
    def normalize_labels(self, df: pd.DataFrame) -> tuple[pd.DataFrame, Optional[str], int, int]:
        """Normalize labels to 0/1 and count normalized/invalid rows"""
        label_col = self._detect_label_column(df)
        if not label_col:
            return df, None, 0, 0
        normalized = 0
        truthy = {"1", "true", "yes", "y", "t"}
        falsy = {"0", "false", "no", "n", "f"}
        def map_label(v):
            nonlocal normalized
            if pd.isna(v):
                return v
            if isinstance(v, (int, np.integer)):
                return 1 if v == 1 else (0 if v == 0 else v)
            if isinstance(v, (float, np.floating)):
                return 1 if int(v) == 1 and v == 1.0 else (0 if int(v) == 0 and v == 0.0 else v)
            s = str(v).strip().lower()
            if s in truthy:
                normalized += 1
                return 1
            if s in falsy:
                normalized += 1
                return 0
            return v
        df[label_col] = df[label_col].apply(map_label)
        invalid_mask = ~df[label_col].isin([0, 1])
        invalid_rows = int(invalid_mask.sum())
        df = df[~invalid_mask]
        df[label_col] = df[label_col].astype('int64')
        return df, label_col, normalized, invalid_rows
    
    def remove_outliers(self, df: pd.DataFrame, threshold: float) -> tuple[pd.DataFrame, int]:
        """Drop rows considered outliers using z-score across numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return df, 0
        z = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std(ddof=0)
        mask = (np.abs(z) > threshold).any(axis=1)
        removed = int(mask.sum())
        df = df[~mask]
        return df, removed
    
    def parse_dates(self, df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
        """Auto-detect and parse date columns"""
        parsed_cols = 0
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Try converting to datetime
                    temp = pd.to_datetime(df[col], errors='coerce')
                    # If more than 50% are valid dates (and not all NaT), accept it
                    valid_ratio = temp.notna().mean()
                    if valid_ratio > 0.5:
                        df[col] = temp
                        parsed_cols += 1
                except Exception:
                    continue
        if parsed_cols > 0:
            logger.info(f"Parsed {parsed_cols} date columns")
        return df, parsed_cols

    def encode_categorical(self, df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
        """Encode categorical variables"""
        strategy = self.config.encoding_strategy
        if strategy not in ["onehot", "label"]:
            return df, 0
            
        encoded_cols = 0
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        # Exclude label column if present
        label_col = self.config.label_column or self._detect_label_column(df)
        if label_col and label_col in cat_cols:
            cat_cols = cat_cols.drop(label_col)
            
        if len(cat_cols) == 0:
            return df, 0
            
        if strategy == "onehot":
            original_len = len(df.columns)
            df = pd.get_dummies(df, columns=cat_cols, dummy_na=False)
            encoded_cols = len(df.columns) - original_len + len(cat_cols) # rough count of changes
        elif strategy == "label":
            for col in cat_cols:
                df[col] = df[col].astype('category').cat.codes
                encoded_cols += 1
                
        logger.info(f"Encoded {len(cat_cols)} columns using {strategy} strategy")
        return df, encoded_cols

    def _generate_column_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate detailed statistics for each column"""
        stats = {}
        for col in df.columns:
            try:
                col_stats = {
                    "dtype": str(df[col].dtype),
                    "missing": int(df[col].isnull().sum()),
                    "unique": int(df[col].nunique())
                }
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_stats.update({
                        "mean": float(df[col].mean()) if not df[col].empty else None,
                        "min": float(df[col].min()) if not df[col].empty else None,
                        "max": float(df[col].max()) if not df[col].empty else None,
                        "std": float(df[col].std()) if not df[col].empty else None
                    })
                stats[str(col)] = col_stats
            except Exception as e:
                logger.error(f"Error generating stats for column {col}: {e}")
                stats[str(col)] = {"error": str(e)}
        return stats

    def calculate_quality_metrics(self, df: pd.DataFrame, 
                                  original_count: int,
                                  report_data: Dict[str, Any] = None) -> QualityMetrics:
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
            issues=issues,
            report=report_data or {}
        )
    
    def process(self, input_path: str, output_path: str) -> QualityMetrics:
        """Main processing pipeline"""
        logger.info(f"Starting tabular data processing: {input_path}")
        
        # Load data
        df = self.load_data(input_path)
        original_count = len(df)
        
        # Initialize stats variables
        first_dupe_removed = 0
        second_dupe_removed = 0
        text_changes = 0
        cleaned_cols = 0
        labels_normalized = 0
        invalid_label_rows = 0
        missing_filled = 0
        normalized_cols = 0
        outliers_removed = 0
        label_col = None
        dates_parsed = 0
        encoded_cols = 0

        # Clean column names
        df = self.clean_column_names(df)
        
        # Remove duplicates
        if self.config.remove_duplicates:
            before = len(df)
            df = self.remove_duplicates(df)
            first_dupe_removed = before - len(df)
        
        # Clean text columns
        if self.config.text_cleaning:
            df, cleaned_cols, text_changes = self.clean_text_columns(df)
        
        # Enforce data types
        if self.config.enforce_data_types:
            df = self.enforce_data_types(df)

        # Parse dates
        if self.config.parse_dates:
            df, dates_parsed = self.parse_dates(df)
        
        # Normalize labels and validate
        if self.config.label_normalization:
            df, label_col, labels_normalized, invalid_label_rows = self.normalize_labels(df)
        
        # Handle missing values
        if self.config.handle_missing_values:
            missing_before = int(df.isnull().sum().sum())
            df = self.handle_missing_values(df)
            missing_after = int(df.isnull().sum().sum())
            missing_filled = max(0, missing_before - missing_after)
        
        # Encode categorical variables
        if self.config.encoding_strategy != "none":
            df, encoded_cols = self.encode_categorical(df)

        # Normalize if requested
        if self.config.normalize_data:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            normalized_cols = len(numeric_cols)
            df = self.normalize_data(df)
        
        # Optional outlier removal
        if self.config.drop_outliers:
            df, outliers_removed = self.remove_outliers(df, self.config.outlier_threshold)
        
        # Remove duplicates again after cleaning
        if self.config.second_duplicate_removal and self.config.remove_duplicates:
            before2 = len(df)
            df = self.remove_duplicates(df)
            second_dupe_removed = before2 - len(df)
        
        # Save processed data (final)
        output_path_obj = Path(output_path)
        if output_path_obj.suffix == '.csv':
            df.to_csv(output_path, index=False)
        elif output_path_obj.suffix in ['.xlsx', '.xls']:
            df.to_excel(output_path, index=False)
        elif output_path_obj.suffix == '.parquet':
            df.to_parquet(output_path, index=False)
        elif output_path_obj.suffix == '.json':
            df.to_json(output_path, orient="records")
        logger.info(f"Saved processed data to: {output_path}")
        
        # Generate detailed report
        report_data = {
            "changes": {
                "rows_removed": (original_count - len(df)),
                "duplicates_removed": first_dupe_removed + second_dupe_removed,
                "missing_filled": missing_filled,
                "outliers_removed": outliers_removed,
                "invalid_labels_dropped": invalid_label_rows,
                "text_cells_cleaned": text_changes,
                "dates_parsed": dates_parsed,
                "encoded_cols": encoded_cols
            },
            "columns": self._generate_column_stats(df)
        }

        # Calculate and return quality metrics
        metrics = self.calculate_quality_metrics(df, original_count, report_data)
        logger.info(f"Quality score: {metrics.quality_score}")
        
        summary = []
        if cleaned_cols > 0:
            summary.append(f"Cleaned text in {cleaned_cols} columns, {text_changes} cells changed")
        if dates_parsed > 0:
            summary.append(f"Parsed {dates_parsed} date columns")
        if encoded_cols > 0:
            summary.append(f"Encoded categorical columns (strategy: {self.config.encoding_strategy})")
        if label_col:
            summary.append(f"Normalized {labels_normalized} label values in '{label_col}'")
            if invalid_label_rows > 0:
                summary.append(f"Dropped {invalid_label_rows} rows with invalid labels")
        if self.config.handle_missing_values and missing_filled > 0:
            summary.append(f"Filled {missing_filled} missing values (strategy: {self.config.missing_value_strategy})")
        if normalized_cols > 0:
            summary.append(f"Normalized {normalized_cols} numeric columns to 0-1")
        if self.config.remove_duplicates:
            if first_dupe_removed > 0:
                summary.append(f"Removed {first_dupe_removed} duplicates (pre-clean)")
            if second_dupe_removed > 0:
                summary.append(f"Removed {second_dupe_removed} duplicates (post-clean)")
        if outliers_removed > 0:
            summary.append(f"Dropped {outliers_removed} outlier rows (z-score>{self.config.outlier_threshold})")
        
        metrics.issues.extend(summary)
        
        return metrics

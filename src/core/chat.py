import pandas as pd
import re
from typing import Dict, Any, List, Optional
from src.core.models import ProcessingJob

class DataChatEngine:
    def __init__(self):
        pass

    def process_query(self, query: str, df: pd.DataFrame, job_info: ProcessingJob) -> str:
        """
        Process a natural language query against the dataframe and job info.
        """
        query = query.lower()
        
        # 1. General Stats
        if any(w in query for w in ['how many rows', 'row count', 'total rows', 'size']):
            return f"The dataset has {len(df):,} rows."
        
        if any(w in query for w in ['how many columns', 'column count', 'total columns', 'features']):
            return f"The dataset has {len(df.columns)} columns: {', '.join(df.columns[:5])}{'...' if len(df.columns)>5 else ''}."
        
        # 2. Missing Values
        if 'missing' in query or 'null' in query:
            total_missing = df.isnull().sum().sum()
            if 'column' in query or 'breakdown' in query:
                missing_by_col = df.isnull().sum()
                missing_cols = missing_by_col[missing_by_col > 0]
                if missing_cols.empty:
                    return "There are no missing values in any column."
                details = ", ".join([f"{col}: {val}" for col, val in missing_cols.items()])
                return f"Missing values by column: {details}."
            return f"There are {total_missing} missing values in total across the dataset."

        # 3. Duplicates
        if 'duplicate' in query:
            dupes = df.duplicated().sum()
            return f"There are {dupes} duplicate rows found."

        # 4. Outliers (if numeric columns exist)
        if 'outlier' in query:
            numeric_cols = df.select_dtypes(include=['number']).columns
            outlier_info = []
            for col in numeric_cols:
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    z_scores = ((col_data - col_data.mean()) / col_data.std()).abs()
                    outliers = (z_scores > 3).sum()
                    if outliers > 0:
                        outlier_info.append(f"{col}: {outliers}")
            
            if not outlier_info:
                return "No statistical outliers (Z-score > 3) detected in numeric columns."
            return f"Outliers detected: {', '.join(outlier_info)}."

        # 5. Column Specific Stats (Mean, Max, Min)
        # Regex to find column names in query
        col_match = None
        for col in df.columns:
            if col.lower() in query:
                col_match = col
                break
        
        if col_match:
            col_data = df[col_match]
            if pd.api.types.is_numeric_dtype(col_data):
                if 'mean' in query or 'average' in query:
                    return f"The mean of '{col_match}' is {col_data.mean():.2f}."
                if 'median' in query:
                    return f"The median of '{col_match}' is {col_data.median():.2f}."
                if 'max' in query or 'highest' in query:
                    return f"The maximum value of '{col_match}' is {col_data.max()}."
                if 'min' in query or 'lowest' in query:
                    return f"The minimum value of '{col_match}' is {col_data.min()}."
                if 'std' in query or 'deviation' in query:
                    return f"The standard deviation of '{col_match}' is {col_data.std():.2f}."
            else:
                if 'unique' in query:
                    return f"The column '{col_match}' has {col_data.nunique()} unique values."
                if 'values' in query:
                    return f"Sample values for '{col_match}': {', '.join(map(str, col_data.head(5).tolist()))}."

        # 6. Job Info
        if 'status' in query:
            return f"The job status is currently: {job_info.status}."
        
        if 'created' in query or 'time' in query:
            return f"The job was created at {job_info.created_at}."

        return "I can help you with stats! Ask about rows, columns, missing values, duplicates, outliers, or specific column stats (mean, max, min)."

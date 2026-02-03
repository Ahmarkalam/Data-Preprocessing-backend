import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import re

@dataclass
class AnalysisResult:
    total_rows: int
    total_columns: int
    column_stats: Dict[str, Any]
    suggestions: Dict[str, Any]  # Maps to ProcessingConfig fields
    warnings: List[str]

class DatasetAnalyzer:
    def __init__(self, sample_size: int = 1000):
        self.sample_size = sample_size

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the dataframe and return stats and suggestions.
        """
        # Work with a sample if dataset is too large for quick analysis
        if len(df) > self.sample_size:
            df_sample = df.sample(n=self.sample_size, random_state=42)
        else:
            df_sample = df

        total_rows = len(df)
        total_columns = len(df.columns)
        
        column_stats = {}
        suggestions = {
            "remove_duplicates": False,
            "handle_missing_values": False,
            "missing_value_strategy": "mean",
            "text_cleaning": False,
            "remove_html": False,
            "remove_emojis": False,
            "normalize_data": False,
            "label_normalization": False,
            "drop_outliers": False
        }
        warnings = []

        # 1. Duplicate Analysis
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            suggestions["remove_duplicates"] = True
            warnings.append(f"Found {duplicate_count} duplicate rows ({duplicate_count/total_rows:.1%}).")

        # 2. Column Analysis
        missing_rows_count = 0
        text_cols_with_html = []
        text_cols_with_emojis = []
        numeric_cols_with_outliers = []
        potential_labels = []

        for col in df_sample.columns:
            col_data = df_sample[col]
            dtype = str(col_data.dtype)
            n_missing = col_data.isnull().sum()
            
            stats = {
                "dtype": dtype,
                "missing": int(n_missing),
                "unique": int(col_data.nunique())
            }
            column_stats[str(col)] = stats

            # Missing Values
            if n_missing > 0:
                suggestions["handle_missing_values"] = True
                missing_rows_count += n_missing

            # Text Analysis
            if pd.api.types.is_string_dtype(col_data):
                # Check for HTML
                if col_data.str.contains(r'<[^>]+>', regex=True).any():
                    text_cols_with_html.append(col)
                    suggestions["text_cleaning"] = True
                    suggestions["remove_html"] = True
                
                # Check for Emojis (simple range check)
                # This regex covers many common emoji ranges
                if col_data.str.contains(r'[^\x00-\x7F]', regex=True).any():
                     # Rough check for non-ascii which often includes emojis in western text
                     # A more precise emoji regex would be better but this is a decent heuristic for "needs cleaning"
                     text_cols_with_emojis.append(col)
                     suggestions["text_cleaning"] = True
                     suggestions["remove_emojis"] = True

                # Check for Label Candidates (low cardinality string columns)
                if 2 <= col_data.nunique() <= 10 and n_missing == 0:
                    potential_labels.append(col)

            # Numeric Analysis
            if pd.api.types.is_numeric_dtype(col_data):
                # Check for Outliers (Z-score > 3)
                if n_missing == 0 and col_data.std() > 0:
                    z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
                    if (z_scores > 3).any():
                        numeric_cols_with_outliers.append(col)
                        suggestions["drop_outliers"] = True
                
                # Check for Normalization needs (large range)
                if col_data.max() > 100 or col_data.min() < -100:
                    suggestions["normalize_data"] = True

        # Refine Suggestions
        if missing_rows_count > 0:
            warnings.append(f"Found missing values in {missing_rows_count} cells.")
            # Simple heuristic for strategy
            suggestions["missing_value_strategy"] = "mean" # Default

        if text_cols_with_html:
            warnings.append(f"HTML tags detected in: {', '.join(map(str, text_cols_with_html))}.")
        
        if text_cols_with_emojis:
            warnings.append(f"Potential special characters/emojis in: {', '.join(map(str, text_cols_with_emojis))}.")

        if numeric_cols_with_outliers:
            warnings.append(f"Outliers detected in: {', '.join(map(str, numeric_cols_with_outliers))}.")

        if potential_labels:
            warnings.append(f"Potential categorical labels: {', '.join(map(str, potential_labels))}.")
            suggestions["label_normalization"] = True
            # We don't auto-set label_column as it's ambiguous which one is the target

        result = AnalysisResult(
            total_rows=total_rows,
            total_columns=total_columns,
            column_stats=column_stats,
            suggestions=suggestions,
            warnings=warnings
        )
        
        return asdict(result)

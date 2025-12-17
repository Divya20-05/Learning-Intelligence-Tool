"""
Data ingestion and validation module
"""

import pandas as pd
import json
from pathlib import Path
from typing import Union
from src.config import REQUIRED_COLUMNS


class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass


def load_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load data from CSV or JSON file with validation
    
    Args:
        file_path: Path to input file (CSV or JSON)
        
    Returns:
        Validated pandas DataFrame
        
    Raises:
        DataValidationError: If data is invalid or missing required columns
    """
    file_path = Path(file_path)
    
    # Check file exists
    if not file_path.exists():
        raise DataValidationError(f"File not found: {file_path}")
    
    # Load based on file extension
    try:
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() == '.json':
            df = pd.read_json(file_path)
        else:
            raise DataValidationError(f"Unsupported file format: {file_path.suffix}. Use .csv or .json")
    except Exception as e:
        raise DataValidationError(f"Error loading file: {str(e)}")
    
    # Validate data
    validate_data(df)
    
    return df


def validate_data(df: pd.DataFrame) -> None:
    """
    Validate that DataFrame has required columns and valid data types
    
    Args:
        df: DataFrame to validate
        
    Raises:
        DataValidationError: If validation fails
    """
    # Check if DataFrame is empty
    if df.empty:
        raise DataValidationError("Input data is empty")
    
    # Check for required columns
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise DataValidationError(
            f"Missing required columns: {', '.join(missing_columns)}\n"
            f"Required columns: {', '.join(REQUIRED_COLUMNS)}"
        )
    
    # Validate data types
    try:
        # Ensure numeric columns are numeric
        df['time_spent'] = pd.to_numeric(df['time_spent'], errors='coerce')
        df['score'] = pd.to_numeric(df['score'], errors='coerce')
        df['chapter_order'] = pd.to_numeric(df['chapter_order'], errors='coerce')
        df['completion_status'] = pd.to_numeric(df['completion_status'], errors='coerce')
        
        # Check for NaN values after conversion
        if df[['time_spent', 'score', 'chapter_order']].isna().any().any():
            raise DataValidationError("Some numeric columns contain invalid values")
            
    except Exception as e:
        raise DataValidationError(f"Data type validation failed: {str(e)}")
    
    # Validate value ranges
    if (df['score'] < 0).any() or (df['score'] > 100).any():
        raise DataValidationError("Score values must be between 0 and 100")
    
    if (df['time_spent'] < 0).any():
        raise DataValidationError("Time spent values must be non-negative")
    
    if (df['chapter_order'] < 1).any():
        raise DataValidationError("Chapter order must start from 1")
    
    # Validate completion status (should be 0 or 1)
    if not df['completion_status'].isin([0, 1]).all():
        raise DataValidationError("Completion status must be 0 or 1")


def validate_input_format(file_path: Union[str, Path]) -> dict:
    """
    Validate input file and return summary statistics
    
    Args:
        file_path: Path to input file
        
    Returns:
        Dictionary with validation results and statistics
    """
    try:
        df = load_data(file_path)
        
        return {
            'valid': True,
            'message': 'Data validation successful',
            'statistics': {
                'total_records': len(df),
                'unique_students': df['student_id'].nunique(),
                'unique_courses': df['course_id'].nunique(),
                'date_range': f"{df['chapter_order'].min()} to {df['chapter_order'].max()}",
                'avg_score': round(df['score'].mean(), 2),
                'avg_time_spent': round(df['time_spent'].mean(), 2)
            }
        }
    except DataValidationError as e:
        return {
            'valid': False,
            'message': str(e),
            'statistics': None
        }

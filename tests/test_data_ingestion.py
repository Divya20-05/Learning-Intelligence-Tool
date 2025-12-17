"""
Tests for data ingestion module
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path

from src.data.ingestion import load_data, validate_data, validate_input_format, DataValidationError


def create_valid_csv(path):
    """Helper to create a valid test CSV"""
    data = {
        'student_id': [1, 1, 2, 2],
        'course_id': [1, 1, 1, 1],
        'chapter_order': [1, 2, 1, 2],
        'time_spent': [30.5, 45.2, 25.0, 50.0],
        'score': [85.0, 90.0, 70.0, 75.0],
        'completion_status': [1, 1, 1, 0]
    }
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    return df


def test_load_valid_csv():
    """Test loading a valid CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        path = Path(f.name)
    
    try:
        create_valid_csv(path)
        df = load_data(path)
        assert len(df) == 4
        assert 'student_id' in df.columns
    finally:
        path.unlink()


def test_load_nonexistent_file():
    """Test loading a file that doesn't exist"""
    with pytest.raises(DataValidationError, match="File not found"):
        load_data("nonexistent_file.csv")


def test_load_invalid_format():
    """Test loading an unsupported file format"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        path = Path(f.name)
        f.write("test")
    
    try:
        with pytest.raises(DataValidationError, match="Unsupported file format"):
            load_data(path)
    finally:
        path.unlink()


def test_validate_missing_columns():
    """Test validation with missing required columns"""
    df = pd.DataFrame({
        'student_id': [1, 2],
        'score': [85, 90]
    })
    
    with pytest.raises(DataValidationError, match="Missing required columns"):
        validate_data(df)


def test_validate_empty_dataframe():
    """Test validation with empty DataFrame"""
    df = pd.DataFrame()
    
    with pytest.raises(DataValidationError, match="Input data is empty"):
        validate_data(df)


def test_validate_invalid_score_range():
    """Test validation with scores outside valid range"""
    df = pd.DataFrame({
        'student_id': [1],
        'course_id': [1],
        'chapter_order': [1],
        'time_spent': [30.0],
        'score': [150.0],  # Invalid: > 100
        'completion_status': [1]
    })
    
    with pytest.raises(DataValidationError, match="Score values must be between 0 and 100"):
        validate_data(df)


def test_validate_negative_time():
    """Test validation with negative time spent"""
    df = pd.DataFrame({
        'student_id': [1],
        'course_id': [1],
        'chapter_order': [1],
        'time_spent': [-10.0],  # Invalid: negative
        'score': [85.0],
        'completion_status': [1]
    })
    
    with pytest.raises(DataValidationError, match="Time spent values must be non-negative"):
        validate_data(df)


def test_validate_input_format_success():
    """Test validate_input_format with valid data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        path = Path(f.name)
    
    try:
        create_valid_csv(path)
        result = validate_input_format(path)
        
        assert result['valid'] is True
        assert result['statistics'] is not None
        assert result['statistics']['total_records'] == 4
        assert result['statistics']['unique_students'] == 2
    finally:
        path.unlink()


def test_validate_input_format_failure():
    """Test validate_input_format with invalid data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        path = Path(f.name)
        # Create invalid CSV (missing columns)
        df = pd.DataFrame({'student_id': [1, 2]})
        df.to_csv(path, index=False)
    
    try:
        result = validate_input_format(path)
        
        assert result['valid'] is False
        assert 'Missing required columns' in result['message']
        assert result['statistics'] is None
    finally:
        path.unlink()

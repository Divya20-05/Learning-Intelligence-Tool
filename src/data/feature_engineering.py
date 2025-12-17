"""
Feature engineering module
"""

import pandas as pd
import numpy as np


def engineer_student_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create student-level features from chapter-level data
    
    Args:
        df: DataFrame with chapter-level data
        
    Returns:
        DataFrame with student-level aggregated features
    """
    # Group by student and course
    student_features = df.groupby(['student_id', 'course_id']).agg({
        'score': ['mean', 'std', 'min', 'max'],
        'time_spent': ['sum', 'mean', 'std'],
        'chapter_order': ['count', 'max'],
        'completion_status': 'sum'
    }).reset_index()
    
    # Flatten column names
    student_features.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                                 for col in student_features.columns.values]
    
    # Rename for clarity
    student_features.rename(columns={
        'score_mean': 'avg_score',
        'score_std': 'score_std',
        'score_min': 'min_score',
        'score_max': 'max_score',
        'time_spent_sum': 'total_time_spent',
        'time_spent_mean': 'avg_time_per_chapter',
        'time_spent_std': 'time_std',
        'chapter_order_count': 'chapters_attempted',
        'chapter_order_max': 'last_chapter',
        'completion_status_sum': 'chapters_completed'
    }, inplace=True)
    
    # Create derived features
    student_features['completion_rate'] = (
        student_features['chapters_completed'] / student_features['chapters_attempted']
    )
    
    # Engagement rate (normalized time spent)
    student_features['engagement_rate'] = (
        student_features['total_time_spent'] / 
        (student_features['chapters_attempted'] * 60)  # Normalize by expected time (60 min/chapter)
    )
    
    # Score trend (difference between last 3 and first 3 chapters)
    score_trend = df.groupby('student_id').apply(_calculate_score_trend).reset_index()
    score_trend.columns = ['student_id', 'score_trend']
    student_features = student_features.merge(score_trend, on='student_id', how='left')
    
    # Low score count (chapters with score < 50)
    low_score_count = df[df['score'] < 50].groupby('student_id').size().reset_index()
    low_score_count.columns = ['student_id', 'low_score_count']
    student_features = student_features.merge(low_score_count, on='student_id', how='left')
    student_features['low_score_count'].fillna(0, inplace=True)
    
    # Fill NaN values in std columns
    student_features['score_std'].fillna(0, inplace=True)
    student_features['time_std'].fillna(0, inplace=True)
    student_features['score_trend'].fillna(0, inplace=True)
    
    return student_features


def engineer_chapter_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create chapter-level features for difficulty analysis
    
    Args:
        df: DataFrame with chapter-level data
        
    Returns:
        DataFrame with chapter-level aggregated features
    """
    # Group by course and chapter
    chapter_features = df.groupby(['course_id', 'chapter_order']).agg({
        'score': ['mean', 'std', 'count'],
        'time_spent': ['mean', 'std'],
        'completion_status': ['sum', 'count']
    }).reset_index()
    
    # Flatten column names
    chapter_features.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                                 for col in chapter_features.columns.values]
    
    # Rename for clarity
    chapter_features.rename(columns={
        'score_mean': 'avg_score',
        'score_std': 'score_std',
        'score_count': 'student_count',
        'time_spent_mean': 'avg_time_spent',
        'time_spent_std': 'time_std',
        'completion_status_sum': 'completions',
        'completion_status_count': 'attempts'
    }, inplace=True)
    
    # Calculate derived metrics
    chapter_features['completion_rate'] = (
        chapter_features['completions'] / chapter_features['attempts']
    )
    
    chapter_features['dropout_rate'] = 1 - chapter_features['completion_rate']
    
    # Fill NaN values
    chapter_features['score_std'].fillna(0, inplace=True)
    chapter_features['time_std'].fillna(0, inplace=True)
    
    return chapter_features


def _calculate_score_trend(group):
    """
    Calculate score trend for a student (improving or declining)
    """
    if len(group) < 4:
        return 0
    
    # Sort by chapter order
    group = group.sort_values('chapter_order')
    
    # Compare first 3 and last 3 chapters
    first_avg = group.head(3)['score'].mean()
    last_avg = group.tail(3)['score'].mean()
    
    return last_avg - first_avg


def prepare_features_for_prediction(df: pd.DataFrame, feature_type: str = 'student') -> pd.DataFrame:
    """
    Prepare features for model prediction
    
    Args:
        df: Raw chapter-level data
        feature_type: 'student' or 'chapter'
        
    Returns:
        Feature DataFrame ready for model input
    """
    if feature_type == 'student':
        return engineer_student_features(df)
    elif feature_type == 'chapter':
        return engineer_chapter_features(df)
    else:
        raise ValueError(f"Invalid feature_type: {feature_type}")

"""
Chapter Difficulty Analyzer
Statistical analysis to identify difficult chapters
"""

import pandas as pd
import numpy as np
from typing import Dict
from src.config import DIFFICULTY_WEIGHTS


class DifficultyAnalyzer:
    """
    Analyzes chapter difficulty using statistical metrics
    (Not ML-based, uses aggregated statistics)
    """
    
    def __init__(self):
        self.weights = DIFFICULTY_WEIGHTS
    
    def analyze_difficulty(self, chapter_features: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate difficulty scores for chapters
        
        Args:
            chapter_features: DataFrame with chapter-level features
            
        Returns:
            DataFrame with difficulty scores and rankings
        """
        df = chapter_features.copy()
        
        # Normalize metrics to 0-1 scale
        df['dropout_rate_norm'] = self._normalize(df['dropout_rate'])
        df['avg_time_norm'] = self._normalize(df['avg_time_spent'])
        df['avg_score_norm'] = 1 - self._normalize(df['avg_score'])  # Invert: low score = high difficulty
        df['completion_rate_norm'] = 1 - self._normalize(df['completion_rate'])  # Invert
        
        # Calculate weighted difficulty score
        df['difficulty_score'] = (
            df['dropout_rate_norm'] * self.weights['dropout_rate'] +
            df['avg_time_norm'] * self.weights['avg_time'] +
            df['avg_score_norm'] * self.weights['avg_score'] +
            df['completion_rate_norm'] * self.weights['completion_rate']
        )
        
        # Scale to 0-100
        df['difficulty_score'] = df['difficulty_score'] * 100
        
        # Add difficulty level
        df['difficulty_level'] = pd.cut(
            df['difficulty_score'],
            bins=[0, 33, 66, 100],
            labels=['Easy', 'Medium', 'Hard'],
            include_lowest=True
        )
        
        # Rank chapters by difficulty
        df['difficulty_rank'] = df['difficulty_score'].rank(ascending=False, method='dense').astype(int)
        
        # Select relevant columns
        result = df[[
            'course_id', 'chapter_order', 'difficulty_score', 'difficulty_level',
            'difficulty_rank', 'dropout_rate', 'avg_time_spent', 'avg_score',
            'completion_rate', 'student_count'
        ]].copy()
        
        return result.sort_values('difficulty_score', ascending=False)
    
    def get_difficult_chapters(self, chapter_features: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        Get the most difficult chapters
        
        Args:
            chapter_features: DataFrame with chapter-level features
            top_n: Number of top difficult chapters to return
            
        Returns:
            DataFrame with top difficult chapters
        """
        difficulty_df = self.analyze_difficulty(chapter_features)
        return difficulty_df.head(top_n)
    
    def get_chapters_needing_improvement(self, chapter_features: pd.DataFrame, 
                                         threshold: float = 60.0) -> pd.DataFrame:
        """
        Get chapters that need improvement (difficulty score > threshold)
        
        Args:
            chapter_features: DataFrame with chapter-level features
            threshold: Difficulty score threshold (default 60)
            
        Returns:
            DataFrame with chapters needing improvement
        """
        difficulty_df = self.analyze_difficulty(chapter_features)
        return difficulty_df[difficulty_df['difficulty_score'] >= threshold]
    
    def _normalize(self, series: pd.Series) -> pd.Series:
        """
        Normalize series to 0-1 range using min-max scaling
        
        Args:
            series: Pandas Series to normalize
            
        Returns:
            Normalized series
        """
        min_val = series.min()
        max_val = series.max()
        
        if max_val == min_val:
            return pd.Series(np.zeros(len(series)), index=series.index)
        
        return (series - min_val) / (max_val - min_val)
    
    def get_summary_statistics(self, difficulty_df: pd.DataFrame) -> Dict:
        """
        Get summary statistics for chapter difficulty
        
        Args:
            difficulty_df: DataFrame from analyze_difficulty()
            
        Returns:
            Dictionary with summary statistics
        """
        return {
            'total_chapters': len(difficulty_df),
            'avg_difficulty_score': round(difficulty_df['difficulty_score'].mean(), 2),
            'hard_chapters': len(difficulty_df[difficulty_df['difficulty_level'] == 'Hard']),
            'medium_chapters': len(difficulty_df[difficulty_df['difficulty_level'] == 'Medium']),
            'easy_chapters': len(difficulty_df[difficulty_df['difficulty_level'] == 'Easy']),
            'highest_difficulty': round(difficulty_df['difficulty_score'].max(), 2),
            'lowest_difficulty': round(difficulty_df['difficulty_score'].min(), 2)
        }

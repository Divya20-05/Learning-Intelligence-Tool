"""
Data preprocessing pipeline
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


class DataPreprocessor:
    """
    Handles data cleaning and transformation
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit preprocessor and transform data (for training)
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        df = df.copy()
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Handle outliers
        df = self._handle_outliers(df)
        
        self.is_fitted = True
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data using fitted preprocessor (for inference)
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        df = df.copy()
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Handle outliers (but don't refit)
        df = self._handle_outliers(df)
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values with appropriate imputation
        """
        # For time_spent: fill with median
        if df['time_spent'].isna().any():
            df['time_spent'].fillna(df['time_spent'].median(), inplace=True)
        
        # For score: fill with mean
        if df['score'].isna().any():
            df['score'].fillna(df['score'].mean(), inplace=True)
        
        # For completion_status: fill with 0 (not completed)
        if df['completion_status'].isna().any():
            df['completion_status'].fillna(0, inplace=True)
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle outliers using IQR method (capping, not removal)
        """
        # Handle time_spent outliers
        q1 = df['time_spent'].quantile(0.25)
        q3 = df['time_spent'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = max(0, q1 - 1.5 * iqr)
        upper_bound = q3 + 1.5 * iqr
        df['time_spent'] = df['time_spent'].clip(lower=lower_bound, upper=upper_bound)
        
        # Score is already bounded [0, 100], no need for outlier handling
        
        return df

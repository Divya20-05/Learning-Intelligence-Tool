"""
Course Completion Prediction Model
Binary classification: Will the student complete the course?
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from pathlib import Path
from typing import Tuple, Dict


class CompletionPredictor:
    """
    Predicts whether a student will complete a course
    """
    
    def __init__(self, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            class_weight='balanced'  # Handle imbalanced data
        )
        self.feature_names = None
        self.is_trained = False
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Train the completion prediction model
        
        Args:
            X: Feature DataFrame
            y: Target labels (1 = will complete, 0 = will not complete)
            
        Returns:
            Dictionary with training metrics
        """
        self.feature_names = list(X.columns)
        
        # Train model
        self.model.fit(X, y)
        self.is_trained = True
        
        # Calculate training metrics
        y_pred = self.model.predict(X)
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, zero_division=0),
            'recall': recall_score(y, y_pred, zero_division=0),
            'f1_score': f1_score(y, y_pred, zero_division=0)
        }
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict completion (binary)
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Binary predictions (1 = will complete, 0 = will not)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        return self.model.predict(X[self.feature_names])
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict completion probability
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Probability of completion (0-1)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Return probability of class 1 (completion)
        return self.model.predict_proba(X[self.feature_names])[:, 1]
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance scores
        
        Returns:
            DataFrame with features and their importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def save(self, path: Path) -> None:
        """
        Save model to disk
        
        Args:
            path: Path to save model file
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, path)
    
    @classmethod
    def load(cls, path: Path) -> 'CompletionPredictor':
        """
        Load model from disk
        
        Args:
            path: Path to model file
            
        Returns:
            Loaded CompletionPredictor instance
        """
        model_data = joblib.load(path)
        
        predictor = cls()
        predictor.model = model_data['model']
        predictor.feature_names = model_data['feature_names']
        predictor.is_trained = model_data['is_trained']
        
        return predictor

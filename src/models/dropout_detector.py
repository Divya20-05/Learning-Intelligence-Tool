"""
Dropout Risk Detection Model
Identifies students at risk of dropping out
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from pathlib import Path
from typing import Dict
from src.config import HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD


class DropoutDetector:
    """
    Detects students at risk of dropping out
    """
    
    def __init__(self, random_state=42):
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state
        )
        self.feature_names = None
        self.is_trained = False
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Train the dropout detection model
        
        Args:
            X: Feature DataFrame
            y: Target labels (1 = will dropout, 0 = will not dropout)
            
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
    
    def predict_risk_score(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict dropout risk score (probability)
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Risk scores (0-1, higher = more likely to dropout)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Return probability of class 1 (dropout)
        return self.model.predict_proba(X[self.feature_names])[:, 1]
    
    def predict_risk_level(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict risk level (High/Medium/Low)
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Array of risk levels
        """
        risk_scores = self.predict_risk_score(X)
        
        risk_levels = np.where(
            risk_scores >= HIGH_RISK_THRESHOLD, 'High',
            np.where(risk_scores >= MEDIUM_RISK_THRESHOLD, 'Medium', 'Low')
        )
        
        return risk_levels
    
    def get_high_risk_students(self, X: pd.DataFrame, student_ids: pd.Series) -> pd.DataFrame:
        """
        Get list of high-risk students with their risk scores
        
        Args:
            X: Feature DataFrame
            student_ids: Series of student IDs
            
        Returns:
            DataFrame with high-risk students and scores
        """
        risk_scores = self.predict_risk_score(X)
        risk_levels = self.predict_risk_level(X)
        
        results = pd.DataFrame({
            'student_id': student_ids.values,
            'risk_score': risk_scores,
            'risk_level': risk_levels
        })
        
        # Filter for high and medium risk
        high_risk = results[results['risk_level'].isin(['High', 'Medium'])].copy()
        high_risk = high_risk.sort_values('risk_score', ascending=False)
        
        return high_risk
    
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
    def load(cls, path: Path) -> 'DropoutDetector':
        """
        Load model from disk
        
        Args:
            path: Path to model file
            
        Returns:
            Loaded DropoutDetector instance
        """
        model_data = joblib.load(path)
        
        detector = cls()
        detector.model = model_data['model']
        detector.feature_names = model_data['feature_names']
        detector.is_trained = model_data['is_trained']
        
        return detector

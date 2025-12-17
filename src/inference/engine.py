"""
Inference Engine - Orchestrates model predictions
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Tuple
from src.models.completion_predictor import CompletionPredictor
from src.models.dropout_detector import DropoutDetector
from src.models.difficulty_analyzer import DifficultyAnalyzer
from src.data.preprocessing import DataPreprocessor
from src.data.feature_engineering import engineer_student_features, engineer_chapter_features
from src.config import COMPLETION_MODEL_PATH, DROPOUT_MODEL_PATH


class InferenceEngine:
    """
    Orchestrates all model predictions and analysis
    """
    
    def __init__(self):
        self.completion_predictor = None
        self.dropout_detector = None
        self.difficulty_analyzer = DifficultyAnalyzer()
        self.preprocessor = DataPreprocessor()
        self.models_loaded = False
    
    def load_models(self) -> None:
        """
        Load trained models from disk
        """
        if not COMPLETION_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Completion model not found at {COMPLETION_MODEL_PATH}. "
                "Please run training first."
            )
        
        if not DROPOUT_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Dropout model not found at {DROPOUT_MODEL_PATH}. "
                "Please run training first."
            )
        
        self.completion_predictor = CompletionPredictor.load(COMPLETION_MODEL_PATH)
        self.dropout_detector = DropoutDetector.load(DROPOUT_MODEL_PATH)
        self.models_loaded = True
    
    def predict(self, df: pd.DataFrame) -> Dict:
        """
        Run all predictions on input data
        
        Args:
            df: Raw chapter-level data
            
        Returns:
            Dictionary with all predictions and analysis
        """
        if not self.models_loaded:
            self.load_models()
        
        # Preprocess data
        df_clean = self.preprocessor.transform(df)
        
        # Engineer features
        student_features = engineer_student_features(df_clean)
        chapter_features = engineer_chapter_features(df_clean)
        
        # 1. Course Completion Predictions
        completion_probs = self.completion_predictor.predict_proba(student_features)
        completion_preds = self.completion_predictor.predict(student_features)
        
        student_predictions = student_features[['student_id', 'course_id']].copy()
        student_predictions['completion_probability'] = completion_probs
        student_predictions['will_complete'] = completion_preds
        
        # 2. Dropout Risk Detection
        dropout_scores = self.dropout_detector.predict_risk_score(student_features)
        dropout_levels = self.dropout_detector.predict_risk_level(student_features)
        
        student_predictions['dropout_risk_score'] = dropout_scores
        student_predictions['risk_level'] = dropout_levels
        
        # Get high-risk students
        high_risk_students = self.dropout_detector.get_high_risk_students(
            student_features, 
            student_features['student_id']
        )
        
        # 3. Chapter Difficulty Analysis
        difficulty_analysis = self.difficulty_analyzer.analyze_difficulty(chapter_features)
        difficult_chapters = self.difficulty_analyzer.get_difficult_chapters(chapter_features, top_n=10)
        chapters_needing_improvement = self.difficulty_analyzer.get_chapters_needing_improvement(
            chapter_features, threshold=60.0
        )
        
        # 4. Feature Importance (Key Factors)
        completion_importance = self.completion_predictor.get_feature_importance()
        dropout_importance = self.dropout_detector.get_feature_importance()
        
        return {
            'student_predictions': student_predictions,
            'high_risk_students': high_risk_students,
            'difficulty_analysis': difficulty_analysis,
            'difficult_chapters': difficult_chapters,
            'chapters_needing_improvement': chapters_needing_improvement,
            'completion_feature_importance': completion_importance,
            'dropout_feature_importance': dropout_importance,
            'summary_stats': self._calculate_summary_stats(
                student_predictions, difficulty_analysis
            )
        }
    
    def _calculate_summary_stats(self, student_preds: pd.DataFrame, 
                                  difficulty_df: pd.DataFrame) -> Dict:
        """
        Calculate summary statistics
        """
        return {
            'total_students': len(student_preds),
            'predicted_completions': int(student_preds['will_complete'].sum()),
            'completion_rate': round(student_preds['will_complete'].mean() * 100, 2),
            'high_risk_count': int((student_preds['risk_level'] == 'High').sum()),
            'medium_risk_count': int((student_preds['risk_level'] == 'Medium').sum()),
            'low_risk_count': int((student_preds['risk_level'] == 'Low').sum()),
            'avg_completion_probability': round(student_preds['completion_probability'].mean() * 100, 2),
            'avg_dropout_risk': round(student_preds['dropout_risk_score'].mean() * 100, 2),
            'total_chapters_analyzed': len(difficulty_df),
            'hard_chapters': int((difficulty_df['difficulty_level'] == 'Hard').sum()),
            'medium_chapters': int((difficulty_df['difficulty_level'] == 'Medium').sum()),
            'easy_chapters': int((difficulty_df['difficulty_level'] == 'Easy').sum())
        }

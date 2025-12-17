"""
Tests for ML models
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path

from src.models.completion_predictor import CompletionPredictor
from src.models.dropout_detector import DropoutDetector
from src.models.difficulty_analyzer import DifficultyAnalyzer


def create_sample_features():
    """Create sample feature data for testing"""
    return pd.DataFrame({
        'avg_score': [85.0, 70.0, 90.0, 60.0],
        'score_std': [5.0, 10.0, 3.0, 15.0],
        'min_score': [75.0, 50.0, 85.0, 40.0],
        'max_score': [95.0, 85.0, 95.0, 75.0],
        'total_time_spent': [200.0, 150.0, 220.0, 100.0],
        'avg_time_per_chapter': [40.0, 30.0, 44.0, 20.0],
        'time_std': [5.0, 8.0, 4.0, 10.0],
        'chapters_attempted': [5, 5, 5, 5],
        'last_chapter': [5, 5, 5, 5],
        'chapters_completed': [5, 4, 5, 3],
        'completion_rate': [1.0, 0.8, 1.0, 0.6],
        'engagement_rate': [0.8, 0.6, 0.9, 0.4],
        'score_trend': [5.0, -5.0, 2.0, -10.0],
        'low_score_count': [0, 1, 0, 2]
    })


def test_completion_predictor_training():
    """Test completion predictor training"""
    X = create_sample_features()
    y = pd.Series([1, 1, 1, 0])  # Labels
    
    predictor = CompletionPredictor()
    metrics = predictor.train(X, y)
    
    assert predictor.is_trained
    assert 'accuracy' in metrics
    assert 'f1_score' in metrics
    assert 0 <= metrics['accuracy'] <= 1


def test_completion_predictor_predict():
    """Test completion predictor predictions"""
    X = create_sample_features()
    y = pd.Series([1, 1, 1, 0])
    
    predictor = CompletionPredictor()
    predictor.train(X, y)
    
    predictions = predictor.predict(X)
    
    assert len(predictions) == len(X)
    assert all(p in [0, 1] for p in predictions)


def test_completion_predictor_predict_proba():
    """Test completion predictor probability predictions"""
    X = create_sample_features()
    y = pd.Series([1, 1, 1, 0])
    
    predictor = CompletionPredictor()
    predictor.train(X, y)
    
    probabilities = predictor.predict_proba(X)
    
    assert len(probabilities) == len(X)
    assert all(0 <= p <= 1 for p in probabilities)


def test_completion_predictor_save_load():
    """Test saving and loading completion predictor"""
    X = create_sample_features()
    y = pd.Series([1, 1, 1, 0])
    
    predictor = CompletionPredictor()
    predictor.train(X, y)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / "test_model.joblib"
        predictor.save(model_path)
        
        loaded_predictor = CompletionPredictor.load(model_path)
        
        assert loaded_predictor.is_trained
        assert loaded_predictor.feature_names == predictor.feature_names
        
        # Test predictions are the same
        orig_preds = predictor.predict(X)
        loaded_preds = loaded_predictor.predict(X)
        assert np.array_equal(orig_preds, loaded_preds)


def test_dropout_detector_training():
    """Test dropout detector training"""
    X = create_sample_features()
    y = pd.Series([0, 0, 0, 1])  # Dropout labels
    
    detector = DropoutDetector()
    metrics = detector.train(X, y)
    
    assert detector.is_trained
    assert 'accuracy' in metrics
    assert 0 <= metrics['accuracy'] <= 1


def test_dropout_detector_risk_score():
    """Test dropout detector risk score predictions"""
    X = create_sample_features()
    y = pd.Series([0, 0, 0, 1])
    
    detector = DropoutDetector()
    detector.train(X, y)
    
    risk_scores = detector.predict_risk_score(X)
    
    assert len(risk_scores) == len(X)
    assert all(0 <= score <= 1 for score in risk_scores)


def test_dropout_detector_risk_level():
    """Test dropout detector risk level predictions"""
    X = create_sample_features()
    y = pd.Series([0, 0, 0, 1])
    
    detector = DropoutDetector()
    detector.train(X, y)
    
    risk_levels = detector.predict_risk_level(X)
    
    assert len(risk_levels) == len(X)
    assert all(level in ['High', 'Medium', 'Low'] for level in risk_levels)


def test_difficulty_analyzer():
    """Test difficulty analyzer"""
    chapter_features = pd.DataFrame({
        'course_id': [1, 1, 1, 2, 2],
        'chapter_order': [1, 2, 3, 1, 2],
        'dropout_rate': [0.1, 0.3, 0.5, 0.2, 0.4],
        'avg_time_spent': [30.0, 45.0, 60.0, 35.0, 50.0],
        'avg_score': [85.0, 70.0, 60.0, 80.0, 65.0],
        'completion_rate': [0.9, 0.7, 0.5, 0.8, 0.6],
        'student_count': [100, 100, 100, 50, 50]
    })
    
    analyzer = DifficultyAnalyzer()
    difficulty_df = analyzer.analyze_difficulty(chapter_features)
    
    assert len(difficulty_df) == len(chapter_features)
    assert 'difficulty_score' in difficulty_df.columns
    assert 'difficulty_level' in difficulty_df.columns
    assert 'difficulty_rank' in difficulty_df.columns
    
    # Check difficulty scores are in valid range
    assert all(0 <= score <= 100 for score in difficulty_df['difficulty_score'])
    
    # Check difficulty levels are valid
    assert all(level in ['Easy', 'Medium', 'Hard'] for level in difficulty_df['difficulty_level'])


def test_difficulty_analyzer_get_difficult_chapters():
    """Test getting most difficult chapters"""
    chapter_features = pd.DataFrame({
        'course_id': [1, 1, 1],
        'chapter_order': [1, 2, 3],
        'dropout_rate': [0.1, 0.5, 0.3],
        'avg_time_spent': [30.0, 60.0, 45.0],
        'avg_score': [85.0, 60.0, 70.0],
        'completion_rate': [0.9, 0.5, 0.7],
        'student_count': [100, 100, 100]
    })
    
    analyzer = DifficultyAnalyzer()
    difficult = analyzer.get_difficult_chapters(chapter_features, top_n=2)
    
    assert len(difficult) == 2
    # Most difficult should be first
    assert difficult.iloc[0]['difficulty_score'] >= difficult.iloc[1]['difficulty_score']


def test_model_predict_before_training():
    """Test that models raise error when predicting before training"""
    X = create_sample_features()
    
    predictor = CompletionPredictor()
    with pytest.raises(ValueError, match="Model must be trained"):
        predictor.predict(X)
    
    detector = DropoutDetector()
    with pytest.raises(ValueError, match="Model must be trained"):
        detector.predict_risk_score(X)

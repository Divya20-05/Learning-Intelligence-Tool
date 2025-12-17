"""
Integration tests for inference engine
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path

from src.inference.engine import InferenceEngine
from src.models.completion_predictor import CompletionPredictor
from src.models.dropout_detector import DropoutDetector


def create_test_data():
    """Create test chapter-level data"""
    return pd.DataFrame({
        'student_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
        'course_id': [1, 1, 1, 1, 1, 1, 1, 1, 1],
        'chapter_order': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'time_spent': [30.0, 35.0, 40.0, 25.0, 30.0, 35.0, 45.0, 50.0, 55.0],
        'score': [85.0, 90.0, 88.0, 70.0, 75.0, 72.0, 92.0, 95.0, 93.0],
        'completion_status': [1, 1, 1, 1, 1, 0, 1, 1, 1]
    })


def create_and_train_models(tmpdir):
    """Helper to create and train models for testing"""
    # Create sample training data
    train_data = pd.DataFrame({
        'avg_score': [85.0, 70.0, 90.0, 60.0, 88.0],
        'score_std': [5.0, 10.0, 3.0, 15.0, 4.0],
        'min_score': [75.0, 50.0, 85.0, 40.0, 80.0],
        'max_score': [95.0, 85.0, 95.0, 75.0, 93.0],
        'total_time_spent': [200.0, 150.0, 220.0, 100.0, 210.0],
        'avg_time_per_chapter': [40.0, 30.0, 44.0, 20.0, 42.0],
        'time_std': [5.0, 8.0, 4.0, 10.0, 4.5],
        'chapters_attempted': [5, 5, 5, 5, 5],
        'last_chapter': [5, 5, 5, 5, 5],
        'chapters_completed': [5, 4, 5, 3, 5],
        'completion_rate': [1.0, 0.8, 1.0, 0.6, 1.0],
        'engagement_rate': [0.8, 0.6, 0.9, 0.4, 0.85],
        'score_trend': [5.0, -5.0, 2.0, -10.0, 3.0],
        'low_score_count': [0, 1, 0, 2, 0]
    })
    
    y_completion = pd.Series([1, 1, 1, 0, 1])
    y_dropout = pd.Series([0, 0, 0, 1, 0])
    
    # Train and save models
    completion_model = CompletionPredictor()
    completion_model.train(train_data, y_completion)
    completion_path = Path(tmpdir) / "completion_model.joblib"
    completion_model.save(completion_path)
    
    dropout_model = DropoutDetector()
    dropout_model.train(train_data, y_dropout)
    dropout_path = Path(tmpdir) / "dropout_model.joblib"
    dropout_model.save(dropout_path)
    
    return completion_path, dropout_path


def test_inference_engine_predict(monkeypatch):
    """Test end-to-end inference pipeline"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and train models
        completion_path, dropout_path = create_and_train_models(tmpdir)
        
        # Monkeypatch model paths
        import src.config as config
        monkeypatch.setattr(config, 'COMPLETION_MODEL_PATH', completion_path)
        monkeypatch.setattr(config, 'DROPOUT_MODEL_PATH', dropout_path)
        
        # Create test data
        df = create_test_data()
        
        # Run inference
        engine = InferenceEngine()
        results = engine.predict(df)
        
        # Verify results structure
        assert 'student_predictions' in results
        assert 'high_risk_students' in results
        assert 'difficulty_analysis' in results
        assert 'difficult_chapters' in results
        assert 'summary_stats' in results
        
        # Verify student predictions
        student_preds = results['student_predictions']
        assert len(student_preds) == 3  # 3 unique students
        assert 'completion_probability' in student_preds.columns
        assert 'will_complete' in student_preds.columns
        assert 'dropout_risk_score' in student_preds.columns
        assert 'risk_level' in student_preds.columns
        
        # Verify probabilities are in valid range
        assert all(0 <= p <= 1 for p in student_preds['completion_probability'])
        assert all(0 <= p <= 1 for p in student_preds['dropout_risk_score'])
        
        # Verify difficulty analysis
        difficulty = results['difficulty_analysis']
        assert len(difficulty) > 0
        assert 'difficulty_score' in difficulty.columns
        assert all(0 <= score <= 100 for score in difficulty['difficulty_score'])


def test_inference_engine_summary_stats(monkeypatch):
    """Test summary statistics calculation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        completion_path, dropout_path = create_and_train_models(tmpdir)
        
        import src.config as config
        monkeypatch.setattr(config, 'COMPLETION_MODEL_PATH', completion_path)
        monkeypatch.setattr(config, 'DROPOUT_MODEL_PATH', dropout_path)
        
        df = create_test_data()
        engine = InferenceEngine()
        results = engine.predict(df)
        
        stats = results['summary_stats']
        
        assert 'total_students' in stats
        assert 'predicted_completions' in stats
        assert 'completion_rate' in stats
        assert 'high_risk_count' in stats
        assert 'avg_completion_probability' in stats
        
        # Verify stats are reasonable
        assert stats['total_students'] == 3
        assert 0 <= stats['completion_rate'] <= 100


def test_inference_engine_models_loaded(monkeypatch):
    """Test that models can be loaded successfully"""
    # Since models are now trained, this should work
    import src.config as config
    
    # Verify model files exist
    assert config.COMPLETION_MODEL_PATH.exists(), "Completion model should exist after training"
    assert config.DROPOUT_MODEL_PATH.exists(), "Dropout model should exist after training"
    
    engine = InferenceEngine()
    engine.load_models()
    
    assert engine.models_loaded
    assert engine.completion_predictor is not None
    assert engine.dropout_detector is not None


def test_batch_processing(monkeypatch):
    """Test processing multiple students at once"""
    with tempfile.TemporaryDirectory() as tmpdir:
        completion_path, dropout_path = create_and_train_models(tmpdir)
        
        import src.config as config
        monkeypatch.setattr(config, 'COMPLETION_MODEL_PATH', completion_path)
        monkeypatch.setattr(config, 'DROPOUT_MODEL_PATH', dropout_path)
        
        # Create larger dataset
        students = []
        for student_id in range(1, 21):  # 20 students
            for chapter in range(1, 6):  # 5 chapters each
                students.append({
                    'student_id': student_id,
                    'course_id': 1,
                    'chapter_order': chapter,
                    'time_spent': 30.0 + chapter * 5,
                    'score': 70.0 + chapter * 3,
                    'completion_status': 1
                })
        
        df = pd.DataFrame(students)
        
        engine = InferenceEngine()
        results = engine.predict(df)
        
        # Should process all students
        assert results['summary_stats']['total_students'] == 20
        assert len(results['student_predictions']) == 20

"""
Model Training Script
Train and save ML models for course completion and dropout prediction
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from datetime import datetime

from src.models.completion_predictor import CompletionPredictor
from src.models.dropout_detector import DropoutDetector
from src.data.preprocessing import DataPreprocessor
from src.data.feature_engineering import engineer_student_features
from src.config import (
    COMPLETION_MODEL_PATH, DROPOUT_MODEL_PATH, MODEL_METADATA_PATH,
    DATA_DIR, RANDOM_STATE, TEST_SIZE
)


def prepare_training_data(df: pd.DataFrame):
    """
    Prepare training data with labels
    
    Args:
        df: Raw chapter-level data
        
    Returns:
        Tuple of (features, completion_labels, dropout_labels)
    """
    # Preprocess data
    preprocessor = DataPreprocessor()
    df_clean = preprocessor.fit_transform(df)
    
    # Engineer student-level features
    student_features = engineer_student_features(df_clean)
    
    # Create labels
    # For completion: did student complete all chapters in the course?
    # We'll use completion_rate as proxy: >= 0.9 = completed
    student_features['completed'] = (student_features['completion_rate'] >= 0.9).astype(int)
    
    # For dropout: inverse of completion
    student_features['dropped_out'] = (student_features['completion_rate'] < 0.9).astype(int)
    
    # Separate features and labels
    feature_cols = [
        'avg_score', 'score_std', 'min_score', 'max_score',
        'total_time_spent', 'avg_time_per_chapter', 'time_std',
        'chapters_attempted', 'last_chapter', 'chapters_completed',
        'completion_rate', 'engagement_rate', 'score_trend', 'low_score_count'
    ]
    
    X = student_features[feature_cols].copy()
    y_completion = student_features['completed']
    y_dropout = student_features['dropped_out']
    
    return X, y_completion, y_dropout


def train_models():
    """
    Train all models and save them
    """
    print("=" * 80)
    print("LEARNING INTELLIGENCE TOOL - MODEL TRAINING")
    print("=" * 80)
    print()
    
    # Load training data
    training_data_path = DATA_DIR / "training_data.csv"
    
    if not training_data_path.exists():
        print(f"❌ Training data not found at {training_data_path}")
        print("Please run scripts/generate_data.py first to generate training data.")
        return
    
    print(f"📂 Loading training data from {training_data_path}...")
    df = pd.read_csv(training_data_path)
    print(f"✓ Loaded {len(df)} records for {df['student_id'].nunique()} students")
    print()
    
    # Prepare training data
    print("🔧 Preparing features and labels...")
    X, y_completion, y_dropout = prepare_training_data(df)
    print(f"✓ Prepared {len(X)} student records with {len(X.columns)} features")
    print(f"  Features: {', '.join(X.columns)}")
    print()
    
    # Split data
    print(f"📊 Splitting data (test size: {TEST_SIZE})...")
    X_train, X_test, y_comp_train, y_comp_test = train_test_split(
        X, y_completion, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_completion
    )
    _, _, y_drop_train, y_drop_test = train_test_split(
        X, y_dropout, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_dropout
    )
    print(f"✓ Train set: {len(X_train)} samples, Test set: {len(X_test)} samples")
    print()
    
    # Train Completion Predictor
    print("🤖 Training Course Completion Predictor...")
    completion_predictor = CompletionPredictor(random_state=RANDOM_STATE)
    train_metrics = completion_predictor.train(X_train, y_comp_train)
    
    # Evaluate on test set
    test_preds = completion_predictor.predict(X_test)
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    test_metrics = {
        'accuracy': accuracy_score(y_comp_test, test_preds),
        'precision': precision_score(y_comp_test, test_preds, zero_division=0),
        'recall': recall_score(y_comp_test, test_preds, zero_division=0),
        'f1_score': f1_score(y_comp_test, test_preds, zero_division=0)
    }
    
    print("  Training Metrics:")
    print(f"    Accuracy:  {train_metrics['accuracy']:.4f}")
    print(f"    Precision: {train_metrics['precision']:.4f}")
    print(f"    Recall:    {train_metrics['recall']:.4f}")
    print(f"    F1 Score:  {train_metrics['f1_score']:.4f}")
    print("  Test Metrics:")
    print(f"    Accuracy:  {test_metrics['accuracy']:.4f}")
    print(f"    Precision: {test_metrics['precision']:.4f}")
    print(f"    Recall:    {test_metrics['recall']:.4f}")
    print(f"    F1 Score:  {test_metrics['f1_score']:.4f}")
    
    # Save model
    completion_predictor.save(COMPLETION_MODEL_PATH)
    print(f"✓ Model saved: {COMPLETION_MODEL_PATH}")
    print()
    
    # Train Dropout Detector
    print("🤖 Training Dropout Risk Detector...")
    dropout_detector = DropoutDetector(random_state=RANDOM_STATE)
    dropout_train_metrics = dropout_detector.train(X_train, y_drop_train)
    
    # Evaluate on test set
    dropout_test_preds = dropout_detector.model.predict(X_test)
    dropout_test_metrics = {
        'accuracy': accuracy_score(y_drop_test, dropout_test_preds),
        'precision': precision_score(y_drop_test, dropout_test_preds, zero_division=0),
        'recall': recall_score(y_drop_test, dropout_test_preds, zero_division=0),
        'f1_score': f1_score(y_drop_test, dropout_test_preds, zero_division=0)
    }
    
    print("  Training Metrics:")
    print(f"    Accuracy:  {dropout_train_metrics['accuracy']:.4f}")
    print(f"    Precision: {dropout_train_metrics['precision']:.4f}")
    print(f"    Recall:    {dropout_train_metrics['recall']:.4f}")
    print(f"    F1 Score:  {dropout_train_metrics['f1_score']:.4f}")
    print("  Test Metrics:")
    print(f"    Accuracy:  {dropout_test_metrics['accuracy']:.4f}")
    print(f"    Precision: {dropout_test_metrics['precision']:.4f}")
    print(f"    Recall:    {dropout_test_metrics['recall']:.4f}")
    print(f"    F1 Score:  {dropout_test_metrics['f1_score']:.4f}")
    
    # Save model
    dropout_detector.save(DROPOUT_MODEL_PATH)
    print(f"✓ Model saved: {DROPOUT_MODEL_PATH}")
    print()
    
    # Save metadata
    print("📝 Saving model metadata...")
    metadata = {
        'training_date': datetime.now().isoformat(),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'features': list(X.columns),
        'completion_model': {
            'type': 'RandomForestClassifier',
            'train_metrics': train_metrics,
            'test_metrics': test_metrics
        },
        'dropout_model': {
            'type': 'GradientBoostingClassifier',
            'train_metrics': dropout_train_metrics,
            'test_metrics': dropout_test_metrics
        },
        'random_state': RANDOM_STATE,
        'test_size': TEST_SIZE
    }
    
    with open(MODEL_METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Metadata saved: {MODEL_METADATA_PATH}")
    print()
    
    # Feature importance
    print("📊 Top 5 Most Important Features:")
    print("\nFor Course Completion:")
    comp_importance = completion_predictor.get_feature_importance().head(5)
    for idx, row in comp_importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    print("\nFor Dropout Risk:")
    drop_importance = dropout_detector.get_feature_importance().head(5)
    for idx, row in drop_importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    print()
    print("=" * 80)
    print("✨ Model training complete!")
    print("=" * 80)


if __name__ == "__main__":
    train_models()

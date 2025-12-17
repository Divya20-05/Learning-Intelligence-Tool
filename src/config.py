"""
Configuration management for Learning Intelligence Tool
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Model file paths
COMPLETION_MODEL_PATH = MODELS_DIR / "completion_model.joblib"
DROPOUT_MODEL_PATH = MODELS_DIR / "dropout_model.joblib"
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"

# Feature configuration
REQUIRED_COLUMNS = [
    "student_id",
    "course_id",
    "chapter_order",
    "time_spent",
    "score",
    "completion_status"
]

# Model parameters
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Risk thresholds
HIGH_RISK_THRESHOLD = 0.7  # Dropout probability > 0.7 = High risk
MEDIUM_RISK_THRESHOLD = 0.4  # Dropout probability > 0.4 = Medium risk

# Difficulty score weights
DIFFICULTY_WEIGHTS = {
    "dropout_rate": 0.35,
    "avg_time": 0.25,
    "avg_score": 0.30,
    "completion_rate": 0.10
}

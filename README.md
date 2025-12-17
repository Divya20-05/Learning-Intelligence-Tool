# Learning Intelligence Tool

> **AI-Powered Learning Analytics for Course Completion Prediction and Learner Insights**

A production-ready CLI tool that analyzes learner data to predict course completion, detect students at risk of dropping out, and identify difficult chapters requiring improvement.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Input Format](#input-format)
- [Output Format](#output-format)
- [Model Details](#model-details)
- [Architecture](#architecture)
- [Testing](#testing)
- [AI Usage Disclosure](#ai-usage-disclosure)
- [Project Structure](#project-structure)

---

## 🎯 Overview

The **Learning Intelligence Tool** is an AI-powered system designed for internship and training platforms to provide intelligent predictions and insights for mentors and administrators. It helps identify at-risk students early, understand key factors affecting course completion, and pinpoint chapters that need content improvement.

### What Makes This a Tool (Not a Notebook)?

✅ **Executable CLI** - Run from command line with simple commands  
✅ **Production Architecture** - Modular design with data ingestion, preprocessing, inference, and reporting layers  
✅ **Saved Models** - Pre-trained models loaded for instant predictions  
✅ **Multiple Output Formats** - JSON, CSV, and formatted text reports  
✅ **Comprehensive Testing** - Unit and integration tests for reliability  
✅ **Reproducible** - Deterministic predictions with fixed random seeds  

---

## ✨ Features

### 1. **Course Completion Prediction** 🎓
- Binary classification to predict if a student will complete a course
- Provides completion probability (0-1) for each student
- Uses Random Forest Classifier for robust predictions

### 2. **Early Risk Detection** ⚠️
- Identifies students likely to drop out before they do
- Categorizes risk levels: High, Medium, Low
- Enables proactive intervention and support

### 3. **Chapter Difficulty Detection** 📚
- Analyzes chapters using dropout rate, time spent, and assessment scores
- Ranks chapters by difficulty (0-100 scale)
- Highlights chapters needing content improvement

### 4. **Insight Generation** 💡
- Human-readable reports with actionable recommendations
- Feature importance analysis (what factors matter most)
- Summary statistics and visualizations
- Multiple export formats (text, JSON, CSV)

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone the Repository
```bash
cd learning-intelligence-tool
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Install the Tool
```bash
pip install -e .
```

This installs the tool as a command-line application accessible via `learning-intelligence-tool`.

---

## ⚡ Quick Start

### 1. Generate Sample Data
```bash
python scripts/generate_data.py
```

This creates:
- `data/training_data.csv` - 1000 students with realistic patterns
- `data/sample_input.csv` - 50 students for testing

### 2. Train Models
```bash
python train_models.py
```

This trains and saves:
- Course completion prediction model
- Dropout risk detection model
- Model metadata with performance metrics

### 3. Run Predictions
```bash
learning-intelligence-tool predict -i data/sample_input.csv -f all
```

This generates:
- Text report with insights
- JSON file with all predictions
- CSV files for detailed analysis

---

## 📖 Usage

### Available Commands

#### **1. Predict** - Run AI predictions
```bash
learning-intelligence-tool predict --input <file> [options]
```

**Options:**
- `-i, --input` - Path to CSV or JSON input file (required)
- `-o, --output` - Output directory (default: outputs/)
- `-f, --format` - Output format: text, json, csv, all (default: text)
- `-v, --verbose` - Enable detailed logging

**Examples:**
```bash
# Basic prediction with text output
learning-intelligence-tool predict -i data/sample_input.csv

# Generate all output formats
learning-intelligence-tool predict -i data/sample_input.csv -f all

# Save to custom directory
learning-intelligence-tool predict -i data/sample_input.csv -o my_reports/
```

#### **2. Validate** - Check input data format
```bash
learning-intelligence-tool validate --input <file>
```

**Example:**
```bash
learning-intelligence-tool validate -i data/sample_input.csv
```

#### **3. Analyze** - Comprehensive analysis (equivalent to predict with --format all)
```bash
learning-intelligence-tool analyze --input <file>
```

**Example:**
```bash
learning-intelligence-tool analyze -i data/sample_input.csv
```

---

## 📊 Input Format

The tool accepts **CSV** or **JSON** files with the following required columns:

| Column | Type | Description | Valid Range |
|--------|------|-------------|-------------|
| `student_id` | int/string | Unique student identifier | - |
| `course_id` | int/string | Course identifier | - |
| `chapter_order` | int | Chapter sequence number | ≥ 1 |
| `time_spent` | float | Time spent on chapter (minutes) | ≥ 0 |
| `score` | float | Assessment score | 0-100 |
| `completion_status` | int | Chapter completed (1) or not (0) | 0 or 1 |

### Sample CSV Format
```csv
student_id,course_id,chapter_order,time_spent,score,completion_status
1,101,1,30.5,85.0,1
1,101,2,45.2,90.0,1
1,101,3,38.7,88.0,1
2,101,1,25.0,70.0,1
2,101,2,50.0,65.0,0
```

### Sample JSON Format
```json
[
  {
    "student_id": 1,
    "course_id": 101,
    "chapter_order": 1,
    "time_spent": 30.5,
    "score": 85.0,
    "completion_status": 1
  }
]
```

---

## 📤 Output Format

### Text Report
Formatted console output with:
- Summary statistics (completion rates, risk distribution)
- High-risk students table
- Difficult chapters table
- Key factors affecting completion
- Actionable recommendations

### JSON Report (`predictions.json`)
```json
{
  "summary_stats": {
    "total_students": 50,
    "predicted_completions": 38,
    "completion_rate": 76.0,
    "high_risk_count": 5
  },
  "student_predictions": [
    {
      "student_id": 1,
      "completion_probability": 0.92,
      "will_complete": 1,
      "dropout_risk_score": 0.08,
      "risk_level": "Low"
    }
  ],
  "high_risk_students": [...],
  "difficult_chapters": [...]
}
```

### CSV Reports
Multiple CSV files in `outputs/csv_reports/`:
- `student_predictions.csv` - All student predictions
- `high_risk_students.csv` - At-risk students
- `chapter_difficulty_analysis.csv` - Chapter difficulty scores
- `completion_feature_importance.csv` - Feature importance for completion
- `dropout_feature_importance.csv` - Feature importance for dropout

---

## 🤖 Model Details

### 1. Course Completion Predictor

**Algorithm:** Random Forest Classifier  
**Purpose:** Predict if a student will complete the course  
**Features Used:**
- Average score across chapters
- Score standard deviation and trend
- Total time spent and engagement rate
- Chapters completed and completion rate
- Low score frequency

**Performance Metrics:**
- Accuracy: ~85-90% (on test set)
- F1 Score: ~0.85
- Balanced for imbalanced data using class weights

### 2. Dropout Risk Detector

**Algorithm:** Gradient Boosting Classifier  
**Purpose:** Identify students at risk of dropping out  
**Features Used:**
- Same as completion predictor
- Optimized for early detection

**Risk Levels:**
- **High Risk:** Dropout probability > 70%
- **Medium Risk:** Dropout probability 40-70%
- **Low Risk:** Dropout probability < 40%

**Performance Metrics:**
- Accuracy: ~85-90%
- Recall: Optimized for catching at-risk students

### 3. Chapter Difficulty Analyzer

**Algorithm:** Statistical Analysis (not ML-based)  
**Metrics:**
- Dropout rate per chapter (35% weight)
- Average time spent (25% weight)
- Average score - inverted (30% weight)
- Completion rate - inverted (10% weight)

**Output:** Difficulty score 0-100 and level (Easy/Medium/Hard)

### Feature Importance

Top factors affecting course completion:
1. `completion_rate` - Current progress
2. `avg_score` - Overall performance
3. `engagement_rate` - Time investment
4. `score_trend` - Improving or declining
5. `low_score_count` - Struggling indicators

---

## 🏗️ Architecture

```
┌─────────────────┐
│   CLI Interface │  (Click framework)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Ingestion  │  (CSV/JSON loading, validation)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocessing  │  (Missing values, outliers)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Feature Engineer │  (Aggregation, derived features)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      Inference Engine               │
│  ┌─────────────────────────────┐   │
│  │ Completion Predictor Model  │   │
│  │ Dropout Detector Model      │   │
│  │ Difficulty Analyzer         │   │
│  └─────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│Insight Generator│  (Reports, recommendations)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Output (JSON/   │
│  CSV/Text)      │
└─────────────────┘
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Modules
```bash
# Data ingestion tests
pytest tests/test_data_ingestion.py -v

# Model tests
pytest tests/test_models.py -v

# Integration tests
pytest tests/test_inference.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Test Categories

**Unit Tests:**
- Data validation and loading
- Model training and prediction
- Feature engineering
- Output formatting

**Integration Tests:**
- End-to-end prediction pipeline
- Batch processing
- Error handling

**Sanity Checks:**
- Probabilities in [0, 1] range
- Predictions match expected patterns
- Reproducibility (same input → same output)

---

## 🤝 AI Usage Disclosure

This project was developed with assistance from AI tools. Full transparency is provided in [AI_USAGE_DISCLOSURE.md](AI_USAGE_DISCLOSURE.md).

**Summary:**
- **AI Tools Used:** GitHub Copilot (code suggestions), ChatGPT (documentation review)
- **What was AI-generated:** Boilerplate code, docstrings, some test templates
- **What was independently written:** Core ML logic, feature engineering, architecture design, model selection
- **Verification:** All AI-generated code was reviewed, tested, and validated manually

---

## 📁 Project Structure

```
learning-intelligence-tool/
├── src/
│   ├── cli.py                      # CLI interface
│   ├── config.py                   # Configuration
│   ├── data/
│   │   ├── ingestion.py            # Data loading & validation
│   │   ├── preprocessing.py        # Data cleaning
│   │   └── feature_engineering.py  # Feature creation
│   ├── models/
│   │   ├── completion_predictor.py # Completion model
│   │   ├── dropout_detector.py     # Dropout model
│   │   └── difficulty_analyzer.py  # Difficulty scoring
│   ├── inference/
│   │   └── engine.py               # Inference orchestration
│   └── reporting/
│       └── insights.py             # Report generation
├── models/                         # Saved model files
│   ├── completion_model.joblib
│   ├── dropout_model.joblib
│   └── model_metadata.json
├── data/
│   ├── training_data.csv           # Training dataset
│   └── sample_input.csv            # Sample input
├── tests/                          # Test suite
│   ├── test_data_ingestion.py
│   ├── test_models.py
│   └── test_inference.py
├── scripts/
│   └── generate_data.py            # Data generation
├── outputs/                        # Generated reports
├── train_models.py                 # Model training script
├── requirements.txt
├── setup.py
├── README.md
└── AI_USAGE_DISCLOSURE.md
```

---

## 🎓 Educational Value

This tool demonstrates:
- **Production ML Engineering:** Not just notebooks, but deployable systems
- **Software Design Patterns:** Modular architecture, separation of concerns
- **Testing Best Practices:** Comprehensive test coverage
- **CLI Development:** User-friendly command-line interfaces
- **Data Pipeline Design:** Ingestion → Processing → Inference → Reporting
- **Model Deployment:** Saving, loading, and serving ML models

---

## 📝 License

This project is licensed under the MIT License.

---

## 👤 Author

**AI Kata Submission** - Data Science & Machine Learning Internship Assessment

---

## 🙏 Acknowledgments

- Scikit-learn for ML algorithms
- Click for CLI framework
- Pandas for data manipulation
- The open-source community

---

**Built with ❤️ for learning and production AI deployment**

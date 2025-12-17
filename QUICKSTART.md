# Quick Start Guide

## Installation (3 Steps)

### 1. Install Dependencies
```bash
cd learning-intelligence-tool
pip install -r requirements.txt
pip install -e .
```

### 2. Generate Data & Train Models
```bash
# Generate synthetic training data
python3 scripts/generate_data.py

# Train ML models
python3 train_models.py
```

### 3. Run Predictions
```bash
# Run analysis on sample data
learning-intelligence-tool predict -i data/sample_input.csv -f all
```

---

## Usage Examples

### Validate Input Data
```bash
learning-intelligence-tool validate -i data/sample_input.csv
```

### Generate Text Report
```bash
learning-intelligence-tool predict -i data/sample_input.csv
```

### Generate All Formats (JSON + CSV + Text)
```bash
learning-intelligence-tool predict -i data/sample_input.csv -f all
```

### Comprehensive Analysis
```bash
learning-intelligence-tool analyze -i data/sample_input.csv
```

---

## Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

---

## What You Get

### Predictions
- Course completion probability for each student
- Dropout risk level (High/Medium/Low)
- Chapter difficulty scores

### Insights
- List of high-risk students needing intervention
- Chapters requiring content improvement
- Key factors affecting completion
- Actionable recommendations

### Output Formats
- **Text**: Formatted console report
- **JSON**: `outputs/predictions.json`
- **CSV**: `outputs/csv_reports/*.csv`

---

## Input Format

Your CSV/JSON must have these columns:
- `student_id` - Student identifier
- `course_id` - Course identifier
- `chapter_order` - Chapter number (≥ 1)
- `time_spent` - Minutes spent (≥ 0)
- `score` - Assessment score (0-100)
- `completion_status` - 1 if completed, 0 if not

---

## Project Structure

```
learning-intelligence-tool/
├── src/              # Source code
├── models/           # Trained models
├── data/             # Training & sample data
├── tests/            # Test suite
├── outputs/          # Generated reports
├── README.md         # Full documentation
└── AI_USAGE_DISCLOSURE.md
```

---

## Help

```bash
learning-intelligence-tool --help
learning-intelligence-tool predict --help
```

---

**For full documentation, see [README.md](README.md)**

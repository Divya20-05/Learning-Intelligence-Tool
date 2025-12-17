# Web Application Guide

## 🌐 Running the Web Interface

The Learning Intelligence Tool now includes a **beautiful web interface** that allows users to upload CSV/JSON files and get predictions through their browser!

### Quick Start

1. **Navigate to project directory:**
   ```bash
   cd /Users/adityajatling/Documents/Internship_Tools/learning-intelligence-tool
   ```

2. **Run the web application:**
   ```bash
   python3 app.py
   ```
   
   Or use the run script:
   ```bash
   python3 run_web_app.py
   ```

3. **Open your browser:**
   ```
   http://localhost:5000
   ```

### Features

✨ **Drag & Drop Upload** - Simply drag your CSV/JSON file onto the upload area  
📊 **Real-time Validation** - Instant feedback on data format and statistics  
🤖 **Automatic Predictions** - AI predictions run automatically after upload  
📈 **Interactive Results** - Tabbed interface with multiple views  
💾 **Download Reports** - Get JSON, CSV, or text reports with one click  
🎨 **Premium Design** - Modern, gradient UI with smooth animations  

### Using the Web Interface

1. **Upload File**
   - Click "Choose File" or drag & drop your CSV/JSON file
   - File is automatically validated
   - See data statistics instantly

2. **View Results**
   - **Overview**: Summary statistics and risk distribution
   - **High-Risk Students**: Students needing intervention
   - **Difficult Chapters**: Chapters requiring improvement
   - **Key Factors**: Feature importance rankings
   - **Full Report**: Complete text analysis

3. **Download Reports**
   - Click download buttons to get:
     - JSON report with all predictions
     - Text report for reading
     - ZIP file with all CSV reports

4. **Upload New File**
   - Click "Upload New File" to analyze another dataset

### API Endpoints

The web app also provides REST API endpoints:

- `POST /upload` - Upload and validate file
- `POST /predict` - Run predictions
- `GET /download/<output_dir>/<report_type>` - Download reports
- `GET /health` - Health check

### File Format Requirements

Your CSV/JSON must include these columns:
- `student_id` - Student identifier
- `course_id` - Course identifier  
- `chapter_order` - Chapter number (≥ 1)
- `time_spent` - Minutes spent (≥ 0)
- `score` - Assessment score (0-100)
- `completion_status` - 1 if completed, 0 if not

### Screenshots

The web interface includes:
- 🎨 Beautiful gradient header
- 📤 Drag & drop upload area
- 📊 Interactive statistics cards
- 📑 Tabbed results view
- 💾 One-click downloads
- 📱 Responsive design (works on mobile!)

### Stopping the Server

Press `Ctrl+C` in the terminal to stop the web server.

---

## 🚀 Both Interfaces Available

You now have **two ways** to use the Learning Intelligence Tool:

### 1. Command Line Interface (CLI)
```bash
learning-intelligence-tool predict -i data/sample_input.csv -f all
```
**Best for:** Automation, scripts, batch processing

### 2. Web Interface
```bash
python3 app.py
# Open http://localhost:5000
```
**Best for:** Interactive use, demonstrations, non-technical users

---

**Choose the interface that works best for your needs!**

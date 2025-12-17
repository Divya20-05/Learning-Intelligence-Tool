"""
Flask Web Application for Learning Intelligence Tool
Allows users to upload CSV/JSON files and get predictions
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
from pathlib import Path
import tempfile
import json
from datetime import datetime

from src.data.ingestion import load_data, validate_input_format, DataValidationError
from src.inference.engine import InferenceEngine
from src.reporting.insights import InsightGenerator

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = Path('uploads')
app.config['OUTPUT_FOLDER'] = Path('web_outputs')

# Create directories
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['OUTPUT_FOLDER'].mkdir(exist_ok=True)

# Initialize inference engine
inference_engine = None


def get_inference_engine():
    """Lazy load inference engine"""
    global inference_engine
    if inference_engine is None:
        inference_engine = InferenceEngine()
        inference_engine.load_models()
    return inference_engine


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and validation"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        allowed_extensions = {'.csv', '.json'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file format. Please upload CSV or JSON file.'}), 400
        
        # Save file temporarily
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"upload_{timestamp}{file_ext}"
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(filepath)
        
        # Validate file
        validation_result = validate_input_format(filepath)
        
        if not validation_result['valid']:
            # Clean up
            filepath.unlink()
            return jsonify({'error': validation_result['message']}), 400
        
        # Return success with file info
        return jsonify({
            'success': True,
            'filename': filename,
            'statistics': validation_result['statistics']
        })
    
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/predict', methods=['POST'])
def predict():
    """Run predictions on uploaded file"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        filepath = app.config['UPLOAD_FOLDER'] / filename
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Load data
        df = load_data(filepath)
        
        # Run predictions
        engine = get_inference_engine()
        results = engine.predict(df)
        
        # Generate reports
        generator = InsightGenerator()
        
        # Create output directory for this prediction
        output_dir = app.config['OUTPUT_FOLDER'] / filename.replace('.', '_')
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON report
        json_path = output_dir / 'predictions.json'
        generator.save_json_report(results, json_path)
        
        # Save CSV reports
        csv_dir = output_dir / 'csv_reports'
        generator.save_csv_reports(results, csv_dir)
        
        # Generate text report (without colors for web)
        import re
        text_report = generator.generate_text_report(results)
        clean_report = re.sub(r'\x1b\[[0-9;]*m', '', text_report)  # Remove ANSI codes
        
        # Save text report
        text_path = output_dir / 'analysis_report.txt'
        with open(text_path, 'w') as f:
            f.write(clean_report)
        
        # Prepare response with summary
        response = {
            'success': True,
            'summary': results['summary_stats'],
            'high_risk_students': results['high_risk_students'].head(10).to_dict(orient='records'),
            'difficult_chapters': results['difficult_chapters'].head(5).to_dict(orient='records'),
            'completion_importance': results['completion_feature_importance'].head(5).to_dict(orient='records'),
            'output_dir': str(output_dir.name),
            'text_report': clean_report
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@app.route('/download/<output_dir>/<report_type>')
def download_report(output_dir, report_type):
    """Download generated reports"""
    try:
        base_dir = app.config['OUTPUT_FOLDER'] / output_dir
        
        if report_type == 'json':
            filepath = base_dir / 'predictions.json'
            return send_file(filepath, as_attachment=True, download_name='predictions.json')
        
        elif report_type == 'text':
            filepath = base_dir / 'analysis_report.txt'
            return send_file(filepath, as_attachment=True, download_name='analysis_report.txt')
        
        elif report_type == 'csv':
            # Create a zip file with all CSVs
            import zipfile
            import io
            
            csv_dir = base_dir / 'csv_reports'
            memory_file = io.BytesIO()
            
            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for csv_file in csv_dir.glob('*.csv'):
                    zf.write(csv_file, csv_file.name)
            
            memory_file.seek(0)
            return send_file(
                memory_file,
                mimetype='application/zip',
                as_attachment=True,
                download_name='csv_reports.zip'
            )
        
        else:
            return jsonify({'error': 'Invalid report type'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'models_loaded': inference_engine is not None})


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Learning Intelligence Tool - Web Interface")
    print("=" * 80)
    print("\n📍 Server starting at: http://localhost:5000")
    print("\n💡 Instructions:")
    print("   1. Open http://localhost:5000 in your browser")
    print("   2. Upload a CSV or JSON file with learner data")
    print("   3. Get predictions and download reports")
    print("\n" + "=" * 80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

// Learning Intelligence Tool - Frontend JavaScript

let currentFilename = null;
let currentOutputDir = null;
let resultsData = null;

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    setupFileUpload();
});

// Setup file upload functionality
function setupFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');

    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
}

// Handle file selection
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// Handle file upload
async function handleFile(file) {
    // Validate file type
    const validTypes = ['.csv', '.json'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();

    if (!validTypes.includes(fileExt)) {
        showError('Invalid file type. Please upload a CSV or JSON file.');
        return;
    }

    // Show loading
    showLoading('Uploading and validating file...');

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Upload file
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }

        // Store filename
        currentFilename = data.filename;

        // Show file info
        displayFileInfo(file.name, data.statistics);

        // Hide loading
        hideLoading();

        // Run predictions automatically
        runPredictions();

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Display file information
function displayFileInfo(filename, stats) {
    document.getElementById('fileName').textContent = filename;

    const statsHtml = `
        <div class="stat-item">
            <div class="stat-value">${stats.total_records}</div>
            <div class="stat-label">Total Records</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${stats.unique_students}</div>
            <div class="stat-label">Students</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${stats.unique_courses}</div>
            <div class="stat-label">Courses</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${stats.avg_score.toFixed(1)}</div>
            <div class="stat-label">Avg Score</div>
        </div>
    `;

    document.getElementById('fileStats').innerHTML = statsHtml;
    document.getElementById('fileInfo').style.display = 'block';
    document.getElementById('uploadArea').style.display = 'none';
}

// Run predictions
async function runPredictions() {
    showLoading('Running AI predictions...');

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename: currentFilename })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Prediction failed');
        }

        // Store results
        resultsData = data;
        currentOutputDir = data.output_dir;

        // Display results
        displayResults(data);

        // Hide loading
        hideLoading();

        // Show results section
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Display results
function displayResults(data) {
    // Summary stats
    displaySummaryStats(data.summary);

    // Download buttons
    displayDownloadButtons();

    // Overview tab
    displayOverview(data);

    // High-risk students tab
    displayHighRiskStudents(data.high_risk_students);

    // Difficult chapters tab
    displayDifficultChapters(data.difficult_chapters);

    // Key factors tab
    displayKeyFactors(data.completion_importance);

    // Full report tab
    displayFullReport(data.text_report);
}

// Display summary statistics
function displaySummaryStats(stats) {
    const html = `
        <div class="stat-card">
            <div class="value">${stats.total_students}</div>
            <div class="label">Total Students</div>
        </div>
        <div class="stat-card">
            <div class="value">${stats.completion_rate}%</div>
            <div class="label">Completion Rate</div>
        </div>
        <div class="stat-card">
            <div class="value">${stats.high_risk_count}</div>
            <div class="label">High Risk</div>
        </div>
        <div class="stat-card">
            <div class="value">${stats.medium_risk_count}</div>
            <div class="label">Medium Risk</div>
        </div>
    `;

    document.getElementById('statsGrid').innerHTML = html;
}

// Display download buttons
function displayDownloadButtons() {
    const html = `
        <button class="btn btn-success" onclick="downloadReport('json')">
            📄 Download JSON
        </button>
        <button class="btn btn-success" onclick="downloadReport('text')">
            📝 Download Report
        </button>
        <button class="btn btn-success" onclick="downloadReport('csv')">
            📊 Download CSV
        </button>
    `;

    document.getElementById('downloadButtons').innerHTML = html;
}

// Display overview
function displayOverview(data) {
    const html = `
        <h3>📊 Summary</h3>
        <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin-top: 15px;">
            <p><strong>Total Students Analyzed:</strong> ${data.summary.total_students}</p>
            <p><strong>Predicted Completions:</strong> ${data.summary.predicted_completions} (${data.summary.completion_rate}%)</p>
            <p><strong>Average Completion Probability:</strong> ${data.summary.avg_completion_probability}%</p>
            <p><strong>Average Dropout Risk:</strong> ${data.summary.avg_dropout_risk}%</p>
        </div>
        
        <h3 style="margin-top: 30px;">🎯 Risk Distribution</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
            <div style="background: #fee2e2; padding: 20px; border-radius: 8px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #991b1b;">${data.summary.high_risk_count}</div>
                <div style="color: #991b1b;">High Risk Students</div>
            </div>
            <div style="background: #fef3c7; padding: 20px; border-radius: 8px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #92400e;">${data.summary.medium_risk_count}</div>
                <div style="color: #92400e;">Medium Risk Students</div>
            </div>
            <div style="background: #d1fae5; padding: 20px; border-radius: 8px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #065f46;">${data.summary.low_risk_count}</div>
                <div style="color: #065f46;">Low Risk Students</div>
            </div>
        </div>
        
        <h3 style="margin-top: 30px;">💡 Key Insights</h3>
        <ul style="margin-top: 15px; line-height: 2;">
            <li>${data.summary.high_risk_count} students need immediate intervention</li>
            <li>${data.difficult_chapters.length} chapters identified as difficult</li>
            <li>Completion rate is the strongest predictor of success</li>
        </ul>
    `;

    document.getElementById('overview').innerHTML = html;
}

// Display high-risk students
function displayHighRiskStudents(students) {
    if (students.length === 0) {
        document.getElementById('risk').innerHTML = '<p>No high-risk students identified.</p>';
        return;
    }

    let html = '<h3>⚠️ Students Requiring Immediate Intervention</h3>';
    html += '<table><thead><tr><th>Student ID</th><th>Risk Score</th><th>Risk Level</th></tr></thead><tbody>';

    students.forEach(student => {
        const riskClass = student.risk_level === 'High' ? 'risk-high' : 'risk-medium';
        html += `
            <tr>
                <td>${student.student_id}</td>
                <td>${(student.risk_score * 100).toFixed(2)}%</td>
                <td><span class="risk-badge ${riskClass}">${student.risk_level}</span></td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    document.getElementById('risk').innerHTML = html;
}

// Display difficult chapters
function displayDifficultChapters(chapters) {
    if (chapters.length === 0) {
        document.getElementById('difficulty').innerHTML = '<p>No difficult chapters identified.</p>';
        return;
    }

    let html = '<h3>📚 Chapters Needing Content Improvement</h3>';
    html += '<table><thead><tr><th>Course</th><th>Chapter</th><th>Difficulty Score</th><th>Level</th><th>Avg Score</th></tr></thead><tbody>';

    chapters.forEach(chapter => {
        html += `
            <tr>
                <td>${chapter.course_id}</td>
                <td>${chapter.chapter_order}</td>
                <td>${chapter.difficulty_score.toFixed(2)}</td>
                <td>${chapter.difficulty_level}</td>
                <td>${chapter.avg_score.toFixed(2)}</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    document.getElementById('difficulty').innerHTML = html;
}

// Display key factors
function displayKeyFactors(factors) {
    let html = '<h3>🔑 Top Factors Affecting Course Completion</h3>';
    html += '<table><thead><tr><th>Feature</th><th>Importance</th><th>Impact</th></tr></thead><tbody>';

    factors.forEach(factor => {
        const percentage = (factor.importance * 100).toFixed(2);
        const barWidth = percentage;
        html += `
            <tr>
                <td><code>${factor.feature}</code></td>
                <td>${factor.importance.toFixed(4)}</td>
                <td>
                    <div style="background: #e5e7eb; border-radius: 4px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #6366f1, #8b5cf6); height: 20px; width: ${barWidth}%;"></div>
                    </div>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    document.getElementById('factors').innerHTML = html;
}

// Display full report
function displayFullReport(report) {
    const html = `
        <h3>📄 Complete Analysis Report</h3>
        <div class="report-text">${report}</div>
    `;

    document.getElementById('report').innerHTML = html;
}

// Download report
function downloadReport(type) {
    window.location.href = `/download/${currentOutputDir}/${type}`;
}

// Show tab
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });

    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Activate button
    event.target.classList.add('active');
}

// Reset app
function resetApp() {
    currentFilename = null;
    currentOutputDir = null;
    resultsData = null;

    document.getElementById('fileInput').value = '';
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('uploadSection').style.display = 'block';
}

// Remove file
function removeFile() {
    document.getElementById('fileInput').value = '';
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('uploadArea').style.display = 'block';
    currentFilename = null;
}

// Show loading
function showLoading(message) {
    document.getElementById('loadingText').textContent = message;
    document.getElementById('loadingOverlay').style.display = 'flex';
}

// Hide loading
function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// Show error
function showError(message) {
    alert('❌ Error: ' + message);
}

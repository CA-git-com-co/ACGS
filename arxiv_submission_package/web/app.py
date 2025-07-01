#!/usr/bin/env python3
"""
Academic Submission Web Interface

A simple web interface for academic paper validation and submission preparation.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import json
import zipfile

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from flask import (
        Flask,
        render_template,
        request,
        jsonify,
        send_file,
        flash,
        redirect,
        url_for,
    )
    from werkzeug.utils import secure_filename
    from quality_assurance.submission_validator import (
        SubmissionValidator,
        generate_validation_report,
    )
    from quality_assurance.compliance_checker import (
        ComplianceChecker,
        generate_compliance_report,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please install Flask: pip install flask")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = "academic_submission_tool_secret_key"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max file size

# Configuration
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / "academic_submissions"
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {
    ".tex",
    ".bib",
    ".png",
    ".jpg",
    ".jpeg",
    ".pdf",
    ".eps",
    ".txt",
    ".md",
}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """Main page."""
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_files():
    """Handle file upload."""
    if request.method == "GET":
        return render_template("upload.html")

    if "files" not in request.files:
        flash("No files selected")
        return redirect(request.url)

    files = request.files.getlist("files")

    if not files or all(f.filename == "" for f in files):
        flash("No files selected")
        return redirect(request.url)

    # Create unique submission directory
    submission_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    submission_dir = UPLOAD_FOLDER / submission_id
    submission_dir.mkdir(exist_ok=True)

    uploaded_files = []
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = submission_dir / filename
            file.save(str(file_path))
            uploaded_files.append(filename)

    if not uploaded_files:
        flash("No valid files uploaded")
        return redirect(request.url)

    flash(f"Successfully uploaded {len(uploaded_files)} files")
    return redirect(url_for("validate_submission", submission_id=submission_id))


@app.route("/validate/<submission_id>")
def validate_submission(submission_id):
    """Validate uploaded submission."""
    submission_dir = UPLOAD_FOLDER / submission_id

    if not submission_dir.exists():
        flash("Submission not found")
        return redirect(url_for("index"))

    try:
        # Run validation
        validator = SubmissionValidator(submission_dir)
        report = validator.validate_submission()

        # Convert report to JSON-serializable format
        report_data = {
            "submission_id": submission_id,
            "submission_path": str(submission_dir),
            "timestamp": report.timestamp,
            "overall_status": report.overall_status,
            "compliance_score": report.compliance_score,
            "validation_results": [
                {
                    "check_name": r.check_name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp,
                }
                for r in report.validation_results
            ],
            "recommendations": report.recommendations,
        }

        return render_template("validation_results.html", report=report_data)

    except Exception as e:
        flash(f"Validation error: {str(e)}")
        return redirect(url_for("index"))


@app.route("/compliance/<submission_id>")
def check_compliance(submission_id):
    """Check compliance for specific venue."""
    submission_dir = UPLOAD_FOLDER / submission_id
    venue = request.args.get("venue", "arxiv")

    if not submission_dir.exists():
        flash("Submission not found")
        return redirect(url_for("index"))

    try:
        # Run compliance check
        checker = ComplianceChecker()
        results = checker.check_compliance(str(submission_dir), venue)

        # Convert results to JSON-serializable format
        compliance_data = {
            "submission_id": submission_id,
            "venue": venue,
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "rule_id": r.rule_id,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                }
                for r in results
            ],
        }

        return render_template("compliance_results.html", compliance=compliance_data)

    except Exception as e:
        flash(f"Compliance check error: {str(e)}")
        return redirect(url_for("index"))


@app.route("/download_report/<submission_id>")
def download_report(submission_id):
    """Download validation report."""
    submission_dir = UPLOAD_FOLDER / submission_id

    if not submission_dir.exists():
        return jsonify({"error": "Submission not found"}), 404

    try:
        # Generate validation report
        validator = SubmissionValidator(submission_dir)
        report = validator.validate_submission()

        # Generate report file
        report_path = submission_dir / f"validation_report_{submission_id}.md"
        generate_validation_report(report, str(report_path))

        return send_file(
            str(report_path),
            as_attachment=True,
            download_name=f"validation_report_{submission_id}.md",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/validate", methods=["POST"])
def api_validate():
    """API endpoint for validation."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Handle ZIP file upload
    if file.filename.endswith(".zip"):
        submission_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        submission_dir = UPLOAD_FOLDER / submission_id
        submission_dir.mkdir(exist_ok=True)

        # Extract ZIP file
        zip_path = submission_dir / "submission.zip"
        file.save(str(zip_path))

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(submission_dir)

        # Remove ZIP file
        zip_path.unlink()

        try:
            # Run validation
            validator = SubmissionValidator(submission_dir)
            report = validator.validate_submission()

            return jsonify(
                {
                    "submission_id": submission_id,
                    "overall_status": report.overall_status,
                    "compliance_score": report.compliance_score,
                    "validation_results": [
                        {
                            "check_name": r.check_name,
                            "status": r.status,
                            "message": r.message,
                        }
                        for r in report.validation_results
                    ],
                    "recommendations": report.recommendations,
                }
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Only ZIP files supported for API"}), 400


@app.route("/api/compliance", methods=["POST"])
def api_compliance():
    """API endpoint for compliance checking."""
    data = request.get_json()

    if not data or "submission_id" not in data:
        return jsonify({"error": "submission_id required"}), 400

    submission_id = data["submission_id"]
    venue = data.get("venue", "arxiv")
    submission_dir = UPLOAD_FOLDER / submission_id

    if not submission_dir.exists():
        return jsonify({"error": "Submission not found"}), 404

    try:
        # Run compliance check
        checker = ComplianceChecker()
        results = checker.check_compliance(str(submission_dir), venue)

        return jsonify(
            {
                "venue": venue,
                "results": [
                    {"rule_id": r.rule_id, "status": r.status, "message": r.message}
                    for r in results
                ],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/help")
def help_page():
    """Help and documentation page."""
    return render_template("help.html")


@app.route("/about")
def about_page():
    """About page."""
    return render_template("about.html")


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash("File too large. Maximum size is 50MB.")
    return redirect(url_for("upload_files"))


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template("500.html"), 500


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)

    # Create basic templates if they don't exist
    create_basic_templates(templates_dir)

    print("Starting Academic Submission Web Interface...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)


def create_basic_templates(templates_dir):
    """Create basic HTML templates if they don't exist."""

    # Base template
    base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Academic Submission Tool{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">📄 Academic Submission Tool</a>
            <div class="navbar-nav">
                <a class="nav-link" href="{{ url_for('index') }}">Home</a>
                <a class="nav-link" href="{{ url_for('upload_files') }}">Upload</a>
                <a class="nav-link" href="{{ url_for('help_page') }}">Help</a>
                <a class="nav-link" href="{{ url_for('about_page') }}">About</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-info alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

    # Index template
    index_template = """{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-8 mx-auto">
        <div class="text-center mb-5">
            <h1 class="display-4">📄 Academic Submission Tool</h1>
            <p class="lead">Validate and optimize your academic papers for arXiv and journal submissions</p>
        </div>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">🔍 Validate Submission</h5>
                        <p class="card-text">Upload your paper files and get comprehensive validation results with recommendations for improvement.</p>
                        <a href="{{ url_for('upload_files') }}" class="btn btn-primary">Start Validation</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">📋 Check Compliance</h5>
                        <p class="card-text">Verify compliance with specific venue requirements including arXiv, IEEE, and ACM standards.</p>
                        <a href="{{ url_for('upload_files') }}" class="btn btn-outline-primary">Check Compliance</a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <h3>Features</h3>
                <ul class="list-group">
                    <li class="list-group-item">✅ LaTeX syntax validation</li>
                    <li class="list-group-item">📚 Bibliography completeness check</li>
                    <li class="list-group-item">🖼️ Figure reference validation</li>
                    <li class="list-group-item">📏 arXiv compliance verification</li>
                    <li class="list-group-item">♿ Accessibility compliance</li>
                    <li class="list-group-item">🔄 Reproducibility assessment</li>
                </ul>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""

    # Save templates
    templates = {"base.html": base_template, "index.html": index_template}

    for filename, content in templates.items():
        template_path = templates_dir / filename
        if not template_path.exists():
            with open(template_path, "w") as f:
                f.write(content)

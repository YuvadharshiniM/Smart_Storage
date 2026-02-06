"""
Flask Web UI for SmartStorage
Provides a web interface for scanning and viewing file index.
"""
from flask import Flask, render_template, request, jsonify
import json
import os
import sys
from pathlib import Path
from threading import Thread

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scanner import FileScanner
import config

app = Flask(__name__)

# Global variables to track scan status
scan_status = {
    "is_scanning": False,
    "progress_message": "",
    "files_found": 0
}


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/start-scan', methods=['POST'])
def start_scan():
    """
    API endpoint to start a directory scan.
    Expects JSON body with 'directory' field.
    """
    global scan_status
    
    # Check if already scanning
    if scan_status["is_scanning"]:
        return jsonify({
            "success": False,
            "message": "Scan already in progress"
        }), 400
    
    # Get directory from request
    data = request.get_json()
    directory = data.get('directory', '')
    
    if not directory:
        return jsonify({
            "success": False,
            "message": "No directory provided"
        }), 400
    
    # Validate directory
    if not os.path.exists(directory):
        return jsonify({
            "success": False,
            "message": f"Directory does not exist: {directory}"
        }), 400
    
    if not os.path.isdir(directory):
        return jsonify({
            "success": False,
            "message": f"Path is not a directory: {directory}"
        }), 400
    
    # Start scan in background thread
    thread = Thread(target=perform_scan, args=(directory,))
    thread.start()
    
    return jsonify({
        "success": True,
        "message": "Scan started"
    })


@app.route('/api/scan-status', methods=['GET'])
def get_scan_status():
    """
    API endpoint to get current scan status.
    """
    return jsonify(scan_status)


@app.route('/api/files', methods=['GET'])
def get_files():
    """
    API endpoint to get the list of scanned files from the index.
    """
    try:
        # Check if index file exists
        if not os.path.exists(config.INDEX_FILE_PATH):
            return jsonify({
                "success": True,
                "total_files": 0,
                "files": []
            })
        
        # Read the index file
        with open(config.INDEX_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            "success": True,
            "total_files": data.get("total_files", 0),
            "files": data.get("files", [])
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error reading index file: {str(e)}"
        }), 500


def perform_scan(directory: str):
    """
    Perform the actual directory scan.
    Runs in a background thread.
    
    Args:
        directory (str): Directory path to scan
    """
    global scan_status
    
    try:
        # Set scanning status
        scan_status["is_scanning"] = True
        scan_status["progress_message"] = "Starting scan..."
        scan_status["files_found"] = 0
        
        # Create scanner and start scanning
        scanner = FileScanner()
        
        def progress_callback(message: str):
            """Update progress status."""
            scan_status["progress_message"] = message
            scan_status["files_found"] = scanner.get_file_count()
        
        files = scanner.scan_directory(directory, progress_callback=progress_callback)
        
        # Save to JSON
        scan_status["progress_message"] = "Saving index..."
        save_index_to_json(files)
        
        # Update final status
        scan_status["progress_message"] = f"Scan complete! Found {len(files)} files."
        scan_status["files_found"] = len(files)
    
    except Exception as e:
        scan_status["progress_message"] = f"Error: {str(e)}"
    
    finally:
        scan_status["is_scanning"] = False


def save_index_to_json(files_data: list):
    """
    Save the file index to a JSON file.
    
    Args:
        files_data (list): List of file information dictionaries
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(config.INDEX_FILE_PATH), exist_ok=True)
    
    # Create the index structure
    index_data = {
        "total_files": len(files_data),
        "files": files_data
    }
    
    # Save to JSON
    with open(config.INDEX_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)


def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


# Register the format_size filter for templates
app.jinja_env.filters['format_size'] = format_size


if __name__ == '__main__':
    print("\n" + "="*60)
    print(" SmartStorage - Web UI")
    print("="*60)
    print(f" Server running at: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(" Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )

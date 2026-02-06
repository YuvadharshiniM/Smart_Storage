"""
Configuration file for SmartStorage
Contains shared settings and paths used across the application.
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Data directory path
DATA_DIR = PROJECT_ROOT / "data"

# Index file path
INDEX_FILE_PATH = str(DATA_DIR / "file_index.json")

# Flask configuration
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Default scan directory (can be overridden)
DEFAULT_SCAN_DIR = str(Path.home() / "Documents")

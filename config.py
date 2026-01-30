"""
Configuration module for PDF-Insight application.
Centralizes all paths, settings, and configurable parameters.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Input/Output directories
PENDING_DIR = DATA_DIR / "pending"
PROCESSED_DIR = DATA_DIR / "processed"
IMAGES_DIR = DATA_DIR / "images"
TEXT_DIR = DATA_DIR / "text"

# Metadata storage
METADATA_FILE = BASE_DIR / "complete_metadata.json"

# Logging configuration
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "pdf_insight.log"
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Processing options
EXTRACT_IMAGES = True
EXTRACT_TEXT = True
MOVE_AFTER_PROCESSING = True
SKIP_PROCESSED_FILES = True  # Avoid reprocessing files already in metadata

# Image extraction settings
IMAGE_NAME_TEMPLATE = "{pdf_name}_image_{index}.{ext}"  # Template for extracted image names

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    for directory in [DATA_DIR, PENDING_DIR, PROCESSED_DIR, IMAGES_DIR, LOG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

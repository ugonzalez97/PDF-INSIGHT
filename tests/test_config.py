"""
Tests for config module.
"""
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import config


def test_base_directories_exist():
    """Test that base directories are defined."""
    assert config.BASE_DIR is not None
    assert config.DATA_DIR is not None
    assert isinstance(config.BASE_DIR, Path)
    assert isinstance(config.DATA_DIR, Path)


def test_data_directories_defined():
    """Test that all data directories are defined."""
    assert config.PENDING_DIR is not None
    assert config.PROCESSED_DIR is not None
    assert config.IMAGES_DIR is not None
    assert config.TEXT_DIR is not None


def test_directory_hierarchy():
    """Test that directory hierarchy is correct."""
    # DATA_DIR should be under BASE_DIR
    assert config.DATA_DIR.parent == config.BASE_DIR
    
    # All data subdirectories should be under DATA_DIR
    assert config.PENDING_DIR.parent == config.DATA_DIR
    assert config.PROCESSED_DIR.parent == config.DATA_DIR
    assert config.IMAGES_DIR.parent == config.DATA_DIR
    assert config.TEXT_DIR.parent == config.DATA_DIR


def test_database_file_location():
    """Test that database file is in the correct location."""
    assert config.DATABASE_FILE is not None
    assert config.DATABASE_FILE.parent == config.BASE_DIR
    assert config.DATABASE_FILE.suffix == '.db'


def test_log_configuration():
    """Test that logging is properly configured."""
    assert config.LOG_DIR is not None
    assert config.LOG_FILE is not None
    assert config.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    assert config.LOG_FORMAT is not None


def test_processing_options():
    """Test that processing options are defined."""
    assert isinstance(config.EXTRACT_IMAGES, bool)
    assert isinstance(config.EXTRACT_TEXT, bool)


def test_ensure_directories(temp_dir, monkeypatch):
    """Test that ensure_directories creates all required directories."""
    # Monkeypatch config directories to use temp_dir
    monkeypatch.setattr(config, 'DATA_DIR', temp_dir / 'data')
    monkeypatch.setattr(config, 'PENDING_DIR', temp_dir / 'data' / 'pending')
    monkeypatch.setattr(config, 'PROCESSED_DIR', temp_dir / 'data' / 'processed')
    monkeypatch.setattr(config, 'IMAGES_DIR', temp_dir / 'data' / 'images')
    monkeypatch.setattr(config, 'TEXT_DIR', temp_dir / 'data' / 'text')
    monkeypatch.setattr(config, 'LOG_DIR', temp_dir / 'logs')
    
    # Call ensure_directories
    config.ensure_directories()
    
    # Verify directories were created (note: TEXT_DIR not in ensure_directories)
    assert (temp_dir / 'data').exists()
    assert (temp_dir / 'data' / 'pending').exists()
    assert (temp_dir / 'data' / 'processed').exists()
    assert (temp_dir / 'data' / 'images').exists()
    assert (temp_dir / 'logs').exists()

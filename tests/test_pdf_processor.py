"""
Tests for PDFProcessor class.
"""
import sys
from pathlib import Path
import pytest

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pdf_processor import PDFProcessor


def test_pdf_processor_initialization():
    """Test that PDFProcessor initializes correctly."""
    processor = PDFProcessor()
    assert processor is not None


def test_open_pdf_nonexistent_file(temp_dir):
    """Test opening a non-existent PDF file."""
    nonexistent_pdf = temp_dir / "nonexistent.pdf"
    
    reader = PDFProcessor.open_pdf(nonexistent_pdf)
    
    assert reader is None


def test_get_total_words_mock(mocker):
    """Test word counting through get_total_words method."""
    # Create mock reader
    mock_reader = mocker.Mock()
    mock_page = mocker.Mock()
    mock_page.extract_text.return_value = "hello world test"
    mock_reader.pages = [mock_page]
    
    count = PDFProcessor.get_total_words(mock_reader)
    assert count == 3


def test_get_num_pages_mock(mocker):
    """Test getting number of pages."""
    mock_reader = mocker.Mock()
    mock_reader.pages = [1, 2, 3, 4, 5]
    
    count = PDFProcessor.get_num_pages(mock_reader)
    assert count == 5


def test_generate_hex_id():
    """Test generating hexadecimal IDs from Database class."""
    from database import Database
    
    id1 = Database.generate_hex_id()
    id2 = Database.generate_hex_id()
    
    # Should be 8 characters
    assert len(id1) == 8
    assert len(id2) == 8
    
    # Should be different
    assert id1 != id2
    
    # Should be valid hex
    assert all(c in '0123456789abcdef' for c in id1)
    assert all(c in '0123456789abcdef' for c in id2)

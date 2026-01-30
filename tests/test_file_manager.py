"""
Tests for FileManager class.
"""
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from file_manager import FileManager


def test_get_pdf_files_empty_directory(temp_dir):
    """Test getting PDF files from empty directory."""
    pdf_dir = temp_dir / "pdfs"
    pdf_dir.mkdir()
    
    files = FileManager.get_pdf_files(pdf_dir)
    
    assert files == []


def test_get_pdf_files_with_pdfs(temp_dir):
    """Test getting PDF files from directory with PDFs."""
    pdf_dir = temp_dir / "pdfs"
    pdf_dir.mkdir()
    
    # Create dummy PDF files
    (pdf_dir / "test1.pdf").write_text("dummy")
    (pdf_dir / "test2.pdf").write_text("dummy")
    (pdf_dir / "test3.PDF").write_text("dummy")  # uppercase extension
    
    files = FileManager.get_pdf_files(pdf_dir)
    
    assert len(files) == 3
    assert all(f.suffix.lower() == '.pdf' for f in files)


def test_get_pdf_files_ignores_other_files(temp_dir):
    """Test that non-PDF files are ignored."""
    pdf_dir = temp_dir / "pdfs"
    pdf_dir.mkdir()
    
    # Create various files
    (pdf_dir / "test.pdf").write_text("dummy")
    (pdf_dir / "test.txt").write_text("dummy")
    (pdf_dir / "test.jpg").write_text("dummy")
    (pdf_dir / "test.docx").write_text("dummy")
    
    files = FileManager.get_pdf_files(pdf_dir)
    
    assert len(files) == 1
    assert files[0].suffix == '.pdf'


def test_get_pdf_files_nonexistent_directory(temp_dir):
    """Test getting PDF files from non-existent directory."""
    pdf_dir = temp_dir / "nonexistent"
    
    files = FileManager.get_pdf_files(pdf_dir)
    
    assert files == []


def test_move_file_success(temp_dir):
    """Test successfully moving a file."""
    source_dir = temp_dir / "source"
    dest_dir = temp_dir / "dest"
    source_dir.mkdir()
    
    # Create source file
    source_file = source_dir / "test.pdf"
    source_file.write_text("test content")
    
    # Move file
    result = FileManager.move_file(source_file, dest_dir)
    
    assert result is not None
    assert result.exists()
    assert result.parent == dest_dir
    assert not source_file.exists()
    assert result.read_text() == "test content"


def test_move_file_creates_destination(temp_dir):
    """Test that destination directory is created if it doesn't exist."""
    source_dir = temp_dir / "source"
    dest_dir = temp_dir / "nested" / "dest"
    source_dir.mkdir()
    
    source_file = source_dir / "test.pdf"
    source_file.write_text("test content")
    
    result = FileManager.move_file(source_file, dest_dir)
    
    assert dest_dir.exists()
    assert result.exists()


def test_move_file_existing_destination(temp_dir):
    """Test moving file when destination already exists."""
    source_dir = temp_dir / "source"
    dest_dir = temp_dir / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()
    
    # Create source and destination files
    source_file = source_dir / "test.pdf"
    source_file.write_text("source content")
    
    dest_file = dest_dir / "test.pdf"
    dest_file.write_text("dest content")
    
    # Move should handle existing file
    result = FileManager.move_file(source_file, dest_dir)
    
    # Result should be the destination file
    assert result == dest_file
    # Original file should still exist (since move was skipped)
    assert source_file.exists()


def test_save_text_file_success(temp_dir):
    """Test saving text file using the actual method."""
    text_dir = temp_dir / "text"
    
    text_content = "Sample text content\nLine 2\nLine 3"
    pdf_name = "test.pdf"
    hex_id = "abcd1234"
    
    filename, result = FileManager.save_text_file(pdf_name, text_content, text_dir, hex_id)
    
    assert filename is not None
    assert result is not None
    assert result.exists()
    assert text_content in result.read_text()
    assert hex_id in filename

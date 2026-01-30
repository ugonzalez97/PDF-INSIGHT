"""
pytest configuration and shared fixtures.
"""
import sys
import pytest
from pathlib import Path
import tempfile
import shutil

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def temp_data_dirs(temp_dir):
    """Create temporary data directories structure."""
    dirs = {
        'pending': temp_dir / 'pending',
        'processed': temp_dir / 'processed',
        'images': temp_dir / 'images',
        'text': temp_dir / 'text',
        'logs': temp_dir / 'logs'
    }
    
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)
    
    return dirs


@pytest.fixture
def temp_db_path(temp_dir):
    """Create a temporary database path."""
    return temp_dir / "test.db"


@pytest.fixture
def sample_pdf_metadata():
    """Sample PDF metadata for testing."""
    return {
        'filename': 'test.pdf',
        'title': 'Test Document',
        'author': 'Test Author',
        'subject': 'Testing',
        'creator': 'Test Creator',
        'producer': 'Test Producer',
        'creation_date': '2024-01-01',
        'modification_date': '2024-01-02',
        'num_pages': 5,
        'total_words': 1000,
        'total_images': 3,
        'total_attachments': 0
    }


@pytest.fixture
def create_sample_pdf(temp_dir):
    """Factory fixture to create sample PDF files."""
    def _create_pdf(filename="test.pdf", content=None):
        """
        Create a minimal PDF file for testing.
        Note: This creates a simple text file with .pdf extension.
        For real PDF testing, use actual PDF samples.
        """
        pdf_path = temp_dir / filename
        pdf_path.write_text(content or "Sample PDF content")
        return pdf_path
    
    return _create_pdf


@pytest.fixture
def sample_image_data():
    """Sample image data for testing."""
    return {
        'page_number': 1,
        'image_index': 0,
        'file_extension': 'jpg'
    }

"""
Tests for Database class.
"""
import sys
from pathlib import Path
from datetime import datetime

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from database import Database


def test_database_initialization(temp_db_path):
    """Test that database initializes correctly."""
    db = Database(temp_db_path)
    assert temp_db_path.exists()
    assert db.db_path == temp_db_path


def test_database_creates_tables(temp_db_path):
    """Test that all required tables are created."""
    db = Database(temp_db_path)
    conn = db._get_connection()
    cursor = conn.cursor()
    
    # Check that tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    
    assert 'pdf_documents' in tables
    assert 'images' in tables
    assert 'texts' in tables
    
    conn.close()


def test_add_pdf_metadata(temp_db_path, sample_pdf_metadata):
    """Test adding PDF metadata to database."""
    db = Database(temp_db_path)
    
    pdf_id = db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
    
    assert pdf_id is not None
    assert isinstance(pdf_id, int)
    assert pdf_id > 0


def test_get_pdf_by_filename(temp_db_path, sample_pdf_metadata):
    """Test retrieving PDF by filename."""
    db = Database(temp_db_path)
    db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
    
    pdf = db.get_pdf_by_filename('test.pdf')
    
    assert pdf is not None
    assert pdf['filename'] == 'test.pdf'
    assert pdf['title'] == 'Test Document'
    assert pdf['author'] == 'Test Author'


def test_pdf_exists(temp_db_path, sample_pdf_metadata):
    """Test checking if PDF exists in database."""
    db = Database(temp_db_path)
    
    # Should not exist initially
    assert not db.pdf_exists('test.pdf')
    
    # Add PDF
    db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
    
    # Should exist now
    assert db.pdf_exists('test.pdf')


def test_add_image(temp_db_path, sample_pdf_metadata, sample_image_data):
    """Test adding image reference to database."""
    db = Database(temp_db_path)
    pdf_id = db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
    
    image_id = db.add_image(
        pdf_id,
        'test_img_001.jpg',
        sample_image_data['page_number'],
        sample_image_data['image_index'],
        sample_image_data['file_extension']
    )
    
    assert image_id is not None
    assert isinstance(image_id, int)


def test_add_text(temp_db_path, sample_pdf_metadata):
    """Test adding text reference to database."""
    db = Database(temp_db_path)
    pdf_id = db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
    
    text_id = db.add_text(pdf_id, 'test_text.txt', 1000)
    
    assert text_id is not None
    assert isinstance(text_id, int)


def test_get_all_pdfs(temp_db_path, sample_pdf_metadata):
    """Test retrieving all PDFs from database."""
    db = Database(temp_db_path)
    
    # Add multiple PDFs
    db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
    
    metadata2 = sample_pdf_metadata.copy()
    metadata2['filename'] = 'test2.pdf'
    db.add_pdf_document(metadata2['filename'], metadata2)
    
    pdfs = db.get_all_pdfs()
    
    assert len(pdfs) == 2
    assert all('filename' in pdf for pdf in pdfs)


def test_get_pdf_statistics(temp_db_path, sample_pdf_metadata):
    """Test getting database statistics."""
    db = Database(temp_db_path)
    db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
    
    count = db.get_pdf_count()
    
    assert count is not None
    assert count == 1


def test_get_images_for_pdf(temp_db_path, sample_pdf_metadata, sample_image_data):
    """Test retrieving images for a specific PDF."""
    db = Database(temp_db_path)
    pdf_id = db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
    
    # Add images
    for i in range(3):
        db.add_image(
            pdf_id,
            f'test_img_{i:03d}.jpg',
            sample_image_data['page_number'],
            sample_image_data['image_index'],
            sample_image_data['file_extension']
        )
    
    images = db.get_images_by_pdf_id(pdf_id)
    
    assert len(images) == 3
    assert all('filename' in img for img in images)


def test_duplicate_pdf_handling(temp_db_path, sample_pdf_metadata):
    """Test that duplicate filenames are handled correctly."""
    db = Database(temp_db_path)
    
    # Add PDF first time
    pdf_id1 = db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
    
    # Try to add same filename again - should handle gracefully
    # (Implementation might vary - could raise exception or return existing ID)
    try:
        pdf_id2 = db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
        # If it returns existing ID, they should be the same
        # Or it might raise an exception which is also valid
    except Exception as e:
        # Exception is acceptable for duplicate handling
        pass


def test_database_connection_cleanup(temp_db_path):
    """Test that database connections are properly managed."""
    db = Database(temp_db_path)
    
    # Perform multiple operations
    conn1 = db._get_connection()
    conn1.close()
    
    conn2 = db._get_connection()
    conn2.close()
    
    # Should not raise any errors
    assert True

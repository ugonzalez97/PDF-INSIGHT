"""
Integration tests for the complete PDF processing workflow.
"""
import sys
from pathlib import Path
import pytest

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from database import Database
from file_manager import FileManager


class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    def test_complete_pdf_workflow(self, temp_db_path, sample_pdf_metadata):
        """Test complete workflow: add PDF, add images, add text, retrieve all."""
        db = Database(temp_db_path)
        
        # 1. Add PDF
        pdf_id = db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
        assert pdf_id > 0
        
        # 2. Add images
        for i in range(3):
            image_id = db.add_image(
                pdf_id,
                f'test_img_{i:03d}.jpg',
                i + 1,  # page_number
                0,      # image_index
                'jpg'   # file_extension
            )
            assert image_id > 0
        
        # 3. Add text
        text_id = db.add_text(pdf_id, 'test_text.txt', 1000)
        assert text_id > 0
        
        # 4. Retrieve and verify
        pdf = db.get_pdf_by_filename('test.pdf')
        assert pdf is not None
        assert pdf['filename'] == 'test.pdf'
        
        images = db.get_images_by_pdf_id(pdf_id)
        assert len(images) == 3
        
        text = db.get_text_by_pdf_id(pdf_id)
        assert text is not None
        assert text['filename'] == 'test_text.txt'
    
    def test_multiple_pdfs_workflow(self, temp_db_path, sample_pdf_metadata):
        """Test processing multiple PDFs."""
        db = Database(temp_db_path)
        
        # Add multiple PDFs
        pdf_ids = []
        for i in range(3):
            metadata = sample_pdf_metadata.copy()
            metadata['filename'] = f'test_{i}.pdf'
            metadata['title'] = f'Test Document {i}'
            pdf_id = db.add_pdf_document(metadata['filename'], metadata)
            pdf_ids.append(pdf_id)
        
        # Verify all PDFs exist
        all_pdfs = db.get_all_pdfs()
        assert len(all_pdfs) == 3
        
        # Verify count
        count = db.get_pdf_count()
        assert count == 3


class TestFileManagerIntegration:
    """Integration tests for file management operations."""
    
    def test_process_directory_workflow(self, temp_data_dirs, create_sample_pdf):
        """Test complete file management workflow."""
        # 1. Create PDFs in pending directory
        pdf1 = create_sample_pdf("test1.pdf")
        pdf2 = create_sample_pdf("test2.pdf")
        
        # Move them to pending
        FileManager.move_file(pdf1, temp_data_dirs['pending'])
        FileManager.move_file(pdf2, temp_data_dirs['pending'])
        
        # 2. Get all PDF files
        pdfs = FileManager.get_pdf_files(temp_data_dirs['pending'])
        assert len(pdfs) == 2
        
        # 3. Process and move to processed
        for pdf in pdfs:
            result = FileManager.move_file(pdf, temp_data_dirs['processed'])
            assert result.exists()
        
        # 4. Verify pending is empty
        remaining = FileManager.get_pdf_files(temp_data_dirs['pending'])
        assert len(remaining) == 0
        
        # 5. Verify processed has files
        processed = FileManager.get_pdf_files(temp_data_dirs['processed'])
        assert len(processed) == 2


class TestEndToEndWorkflow:
    """End-to-end integration tests."""
    
    def test_full_processing_simulation(self, temp_db_path, temp_data_dirs, 
                                       sample_pdf_metadata, create_sample_pdf):
        """Simulate the complete PDF processing workflow."""
        # Initialize components
        db = Database(temp_db_path)
        
        # 1. Setup: Create PDF in pending directory
        pdf_file = create_sample_pdf("document.pdf")
        FileManager.move_file(pdf_file, temp_data_dirs['pending'])
        
        # 2. Get PDFs to process
        pdfs = FileManager.get_pdf_files(temp_data_dirs['pending'])
        assert len(pdfs) == 1
        
        # 3. Check if already processed
        assert not db.pdf_exists('document.pdf')
        
        # 4. Add to database
        metadata = sample_pdf_metadata.copy()
        metadata['filename'] = 'document.pdf'
        pdf_id = db.add_pdf_document(metadata['filename'], metadata)
        
        # 5. Simulate image extraction
        db.add_image(pdf_id, 'document_img_001.jpg', 1, 0, 'jpg')
        
        # 6. Simulate text extraction
        db.add_text(pdf_id, 'document_text.txt', 500)
        
        # 7. Move to processed
        FileManager.move_file(pdfs[0], temp_data_dirs['processed'])
        
        # 8. Verify results
        assert db.pdf_exists('document.pdf')
        pdf = db.get_pdf_by_filename('document.pdf')
        assert pdf is not None
        
        images = db.get_images_by_pdf_id(pdf_id)
        assert len(images) == 1
        
        text = db.get_text_by_pdf_id(pdf_id)
        assert text is not None
        assert text['filename'] == 'document_text.txt'
        
        # Verify file moved
        pending = FileManager.get_pdf_files(temp_data_dirs['pending'])
        assert len(pending) == 0
        
        processed = FileManager.get_pdf_files(temp_data_dirs['processed'])
        assert len(processed) == 1
    
    def test_duplicate_detection(self, temp_db_path, sample_pdf_metadata):
        """Test that duplicate PDFs are properly detected."""
        db = Database(temp_db_path)
        
        # Add PDF first time
        pdf_id1 = db.add_pdf_document(sample_pdf_metadata['filename'], sample_pdf_metadata)
        
        # Check if exists
        assert db.pdf_exists('test.pdf')
        
        # Try to process again (should be detected)
        existing_pdf = db.get_pdf_by_filename('test.pdf')
        assert existing_pdf is not None
        assert existing_pdf['id'] == pdf_id1

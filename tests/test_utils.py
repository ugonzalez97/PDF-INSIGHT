"""
Tests for utils module.
"""
import pytest
from pathlib import Path
import tempfile
import shutil
import json
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


@pytest.fixture
def mock_pdf_reader():
    """Create a mock PdfReader object."""
    reader = Mock()
    
    # Mock metadata
    metadata = Mock()
    metadata.title = "Test Document"
    metadata.author = "Test Author"
    metadata.subject = "Test Subject"
    metadata.creator = "Test Creator"
    metadata.producer = "Test Producer"
    metadata.creation_date = datetime(2024, 1, 1, 12, 0, 0)
    metadata.modification_date = datetime(2024, 1, 2, 12, 0, 0)
    reader.metadata = metadata
    
    # Mock pages
    page1 = Mock()
    page1.extract_text.return_value = "This is page one with ten words total."
    page1.images = []
    
    page2 = Mock()
    page2.extract_text.return_value = "Page two has some more text content here."
    page2.images = []
    
    reader.pages = [page1, page2]
    reader.attachments = None
    
    return reader


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


class TestGetBasicMetadata:
    """Tests for get_basic_metadata function."""
    
    def test_get_basic_metadata(self, mock_pdf_reader):
        """Test extracting basic metadata."""
        from utils import get_basic_metadata
        
        metadata = get_basic_metadata(mock_pdf_reader)
        
        assert metadata["title"] == "Test Document"
        assert metadata["author"] == "Test Author"
        assert metadata["subject"] == "Test Subject"
        assert metadata["creator"] == "Test Creator"
        assert metadata["producer"] == "Test Producer"
        assert "creation_date" in metadata
        assert "modification_date" in metadata
    
    def test_get_basic_metadata_none_values(self):
        """Test handling None values in metadata."""
        from utils import get_basic_metadata
        
        reader = Mock()
        metadata = Mock()
        metadata.title = None
        metadata.author = None
        metadata.subject = None
        metadata.creator = None
        metadata.producer = None
        metadata.creation_date = None
        metadata.modification_date = None
        reader.metadata = metadata
        
        result = get_basic_metadata(reader)
        
        assert result["title"] is None
        assert result["author"] is None
        assert result["subject"] is None
        assert result["creator"] is None
        assert result["producer"] is None
    
    def test_get_basic_metadata_datetime_conversion(self):
        """Test that datetime objects are converted to ISO format."""
        from utils import get_basic_metadata
        
        reader = Mock()
        metadata = Mock()
        metadata.title = "Test"
        metadata.author = "Author"
        metadata.subject = "Subject"
        metadata.creator = "Creator"
        metadata.producer = "Producer"
        test_date = datetime(2024, 1, 15, 10, 30, 45)
        metadata.creation_date = test_date
        metadata.modification_date = test_date
        reader.metadata = metadata
        
        result = get_basic_metadata(reader)
        
        assert result["creation_date"] == test_date.isoformat()
        assert result["modification_date"] == test_date.isoformat()


class TestGetNumPages:
    """Tests for get_num_pages function."""
    
    def test_get_num_pages(self, mock_pdf_reader):
        """Test getting number of pages."""
        from utils import get_num_pages
        
        result = get_num_pages(mock_pdf_reader)
        
        assert result == {"num_pages": 2}
    
    def test_get_num_pages_empty_pdf(self):
        """Test with PDF with no pages."""
        from utils import get_num_pages
        
        reader = Mock()
        reader.pages = []
        
        result = get_num_pages(reader)
        
        assert result == {"num_pages": 0}
    
    def test_get_num_pages_large_pdf(self):
        """Test with PDF with many pages."""
        from utils import get_num_pages
        
        reader = Mock()
        reader.pages = [Mock() for _ in range(100)]
        
        result = get_num_pages(reader)
        
        assert result == {"num_pages": 100}


class TestGetTotalWords:
    """Tests for get_total_words function."""
    
    def test_get_total_words(self, mock_pdf_reader):
        """Test counting total words."""
        from utils import get_total_words
        
        result = get_total_words(mock_pdf_reader)
        
        # "This is page one with ten words total." = 8 words
        # "Page two has some more text content here." = 8 words
        # Total = 16 words
        assert result == {"total_words": 16}
    
    def test_get_total_words_empty_text(self):
        """Test with pages that have no text."""
        from utils import get_total_words
        
        reader = Mock()
        page1 = Mock()
        page1.extract_text.return_value = ""
        page2 = Mock()
        page2.extract_text.return_value = None
        reader.pages = [page1, page2]
        
        result = get_total_words(reader)
        
        assert result == {"total_words": 0}
    
    def test_get_total_words_multiple_spaces(self):
        """Test word counting with multiple spaces."""
        from utils import get_total_words
        
        reader = Mock()
        page = Mock()
        page.extract_text.return_value = "word1   word2    word3"
        reader.pages = [page]
        
        result = get_total_words(reader)
        
        # split() handles multiple spaces correctly
        assert result == {"total_words": 3}
    
    def test_get_total_words_special_characters(self):
        """Test word counting with special characters."""
        from utils import get_total_words
        
        reader = Mock()
        page = Mock()
        page.extract_text.return_value = "test@email.com is-hyphenated word's"
        reader.pages = [page]
        
        result = get_total_words(reader)
        
        # split() counts these as separate tokens
        assert result["total_words"] > 0


class TestGetImageCount:
    """Tests for get_image_count function."""
    
    def test_get_image_count_no_images(self, mock_pdf_reader):
        """Test counting images when there are none."""
        from utils import get_image_count
        
        result = get_image_count(mock_pdf_reader)
        
        assert result == {"total_images": 0}
    
    def test_get_image_count_with_images(self):
        """Test counting images when present."""
        from utils import get_image_count
        
        reader = Mock()
        page1 = Mock()
        page1.images = [Mock(), Mock()]  # 2 images
        page2 = Mock()
        page2.images = [Mock()]  # 1 image
        reader.pages = [page1, page2]
        
        result = get_image_count(reader)
        
        assert result == {"total_images": 3}
    
    def test_get_image_count_mixed_pages(self):
        """Test with some pages having images and some not."""
        from utils import get_image_count
        
        reader = Mock()
        page1 = Mock()
        page1.images = [Mock(), Mock(), Mock()]
        page2 = Mock()
        page2.images = []
        page3 = Mock()
        page3.images = [Mock()]
        reader.pages = [page1, page2, page3]
        
        result = get_image_count(reader)
        
        assert result == {"total_images": 4}


class TestGetAttachmentCount:
    """Tests for get_attachment_count function."""
    
    def test_get_attachment_count_none(self):
        """Test with no attachments."""
        from utils import get_attachment_count
        
        reader = Mock()
        reader.attachments = None
        
        result = get_attachment_count(reader)
        
        assert result == {"total_attachments": 0}
    
    def test_get_attachment_count_empty_list(self):
        """Test with empty attachments list."""
        from utils import get_attachment_count
        
        reader = Mock()
        reader.attachments = []
        
        result = get_attachment_count(reader)
        
        assert result == {"total_attachments": 0}
    
    def test_get_attachment_count_with_attachments(self):
        """Test with attachments present."""
        from utils import get_attachment_count
        
        reader = Mock()
        reader.attachments = [Mock(), Mock(), Mock()]
        
        result = get_attachment_count(reader)
        
        assert result == {"total_attachments": 3}


class TestAppendMetadataToJson:
    """Tests for append_metadata_to_json function."""
    
    def test_append_metadata_to_json_new_file(self, temp_output_dir):
        """Test creating new metadata JSON file."""
        from utils import append_metadata_to_json
        
        file_path = temp_output_dir / "test_metadata.json"
        metadata = {"title": "Test", "author": "Author"}
        
        append_metadata_to_json("test.pdf", metadata, str(file_path))
        
        assert file_path.exists()
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert "test.pdf" in data[0]
    
    def test_append_metadata_to_json_existing_file(self, temp_output_dir):
        """Test appending to existing metadata file."""
        from utils import append_metadata_to_json
        
        file_path = temp_output_dir / "test_metadata.json"
        
        # Add first entry
        metadata1 = {"title": "Test1"}
        append_metadata_to_json("test1.pdf", metadata1, str(file_path))
        
        # Add second entry
        metadata2 = {"title": "Test2"}
        append_metadata_to_json("test2.pdf", metadata2, str(file_path))
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert "test1.pdf" in data[0]
        assert "test2.pdf" in data[1]
    
    def test_append_metadata_to_json_corrupt_file(self, temp_output_dir):
        """Test handling corrupt JSON file."""
        from utils import append_metadata_to_json
        
        file_path = temp_output_dir / "test_metadata.json"
        
        # Create corrupt JSON file
        with open(file_path, 'w') as f:
            f.write("not valid json{{{")
        
        # Should create new file starting fresh
        metadata = {"title": "Test"}
        append_metadata_to_json("test.pdf", metadata, str(file_path))
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
    
    def test_append_metadata_to_json_non_list_data(self, temp_output_dir):
        """Test handling file with non-list JSON data."""
        from utils import append_metadata_to_json
        
        file_path = temp_output_dir / "test_metadata.json"
        
        # Create file with dict instead of list
        with open(file_path, 'w') as f:
            json.dump({"some": "data"}, f)
        
        # Should convert to list and append
        metadata = {"title": "Test"}
        append_metadata_to_json("test.pdf", metadata, str(file_path))
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 2  # Original dict + new entry


class TestExtractImagesFromPdf:
    """Tests for extract_images_from_pdf function."""
    
    def test_extract_images_basic(self, temp_output_dir):
        """Test basic image extraction."""
        from utils import extract_images_from_pdf
        
        # Create mock reader with images
        reader = Mock()
        page1 = Mock()
        
        # Mock image
        img1 = Mock()
        img1.data = b"fake image data"
        img1.name = "jpg"
        
        page1.images = [img1]
        reader.pages = [page1]
        
        extract_images_from_pdf(reader, "test.pdf", str(temp_output_dir))
        
        # Check image was saved
        expected_filename = "test_page1_img1.jpg"
        expected_path = temp_output_dir / expected_filename
        assert expected_path.exists()
    
    def test_extract_images_creates_directory(self, temp_output_dir):
        """Test that output directory is created if it doesn't exist."""
        from utils import extract_images_from_pdf
        
        output_dir = temp_output_dir / "new_images"
        assert not output_dir.exists()
        
        reader = Mock()
        page = Mock()
        img = Mock()
        img.data = b"fake image data"
        img.name = "png"
        page.images = [img]
        reader.pages = [page]
        
        extract_images_from_pdf(reader, "test.pdf", str(output_dir))
        
        assert output_dir.exists()
    
    def test_extract_images_multiple_pages(self, temp_output_dir):
        """Test extracting images from multiple pages."""
        from utils import extract_images_from_pdf
        
        reader = Mock()
        
        # Page 1 with 2 images
        page1 = Mock()
        img1 = Mock()
        img1.data = b"image1"
        img1.name = "jpg"
        img2 = Mock()
        img2.data = b"image2"
        img2.name = "png"
        page1.images = [img1, img2]
        
        # Page 2 with 1 image
        page2 = Mock()
        img3 = Mock()
        img3.data = b"image3"
        img3.name = "jpg"
        page2.images = [img3]
        
        reader.pages = [page1, page2]
        
        extract_images_from_pdf(reader, "test.pdf", str(temp_output_dir))
        
        # Check all images were saved
        assert (temp_output_dir / "test_page1_img1.jpg").exists()
        assert (temp_output_dir / "test_page1_img2.png").exists()
        assert (temp_output_dir / "test_page2_img1.jpg").exists()
    
    def test_extract_images_no_images(self, temp_output_dir):
        """Test with PDF that has no images."""
        from utils import extract_images_from_pdf
        
        reader = Mock()
        page = Mock()
        page.images = []
        reader.pages = [page]
        
        extract_images_from_pdf(reader, "test.pdf", str(temp_output_dir))
        
        # Should not crash and directory should be created
        assert (temp_output_dir).exists()
        # No image files should be created
        image_files = list(temp_output_dir.glob("*.jpg")) + list(temp_output_dir.glob("*.png"))
        assert len(image_files) == 0
    
    def test_extract_images_filename_without_extension(self, temp_output_dir):
        """Test with filename that already has no extension."""
        from utils import extract_images_from_pdf
        
        reader = Mock()
        page = Mock()
        img = Mock()
        img.data = b"image"
        img.name = "jpg"
        page.images = [img]
        reader.pages = [page]
        
        extract_images_from_pdf(reader, "test", str(temp_output_dir))
        
        # Should work correctly
        assert (temp_output_dir / "test_page1_img1.jpg").exists()


class TestIntegration:
    """Integration tests for utils functions."""
    
    def test_complete_metadata_extraction(self, mock_pdf_reader):
        """Test extracting all metadata together."""
        from utils import (
            get_basic_metadata,
            get_num_pages,
            get_total_words,
            get_image_count,
            get_attachment_count
        )
        
        complete_metadata = {}
        complete_metadata.update(get_basic_metadata(mock_pdf_reader))
        complete_metadata.update(get_num_pages(mock_pdf_reader))
        complete_metadata.update(get_total_words(mock_pdf_reader))
        complete_metadata.update(get_image_count(mock_pdf_reader))
        complete_metadata.update(get_attachment_count(mock_pdf_reader))
        
        # Verify all expected keys are present
        expected_keys = [
            'title', 'author', 'subject', 'creator', 'producer',
            'creation_date', 'modification_date', 'num_pages',
            'total_words', 'total_images', 'total_attachments'
        ]
        
        for key in expected_keys:
            assert key in complete_metadata

"""
Tests for web_api module (FastAPI application).
"""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    # Mock config before importing web_api
    with patch('web_api.config') as mock_config:
        # Setup mock config
        temp_dir = Path(tempfile.mkdtemp())
        mock_config.DATABASE_FILE = temp_dir / "test.db"
        mock_config.PENDING_DIR = temp_dir / "pending"
        mock_config.PROCESSED_DIR = temp_dir / "processed"
        mock_config.IMAGES_DIR = temp_dir / "images"
        mock_config.TEXT_DIR = temp_dir / "text"
        mock_config.SKIP_PROCESSED_FILES = True
        mock_config.EXTRACT_IMAGES = True
        mock_config.EXTRACT_TEXT = True
        mock_config.MOVE_AFTER_PROCESSING = False
        mock_config.HEX_ID_LENGTH = 8
        mock_config.IMAGE_NAME_TEMPLATE = "{original_name}_{hex_id}_page{page_num}_img{img_index}.{extension}"
        
        # Create directories
        for dir_path in [mock_config.PENDING_DIR, mock_config.PROCESSED_DIR, 
                         mock_config.IMAGES_DIR, mock_config.TEXT_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        from web_api import app
        client = TestClient(app)
        
        yield client
        
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@pytest.fixture
def mock_db():
    """Mock database for testing."""
    with patch('web_api.db') as mock:
        yield mock


@pytest.fixture
def mock_embeddings_manager():
    """Mock embeddings manager for testing."""
    with patch('web_api.get_embeddings_manager') as mock:
        manager = MagicMock()
        mock.return_value = manager
        yield manager


class TestHTMLViews:
    """Tests for HTML view routes."""
    
    def test_home_page(self, test_client):
        """Test home page returns 200."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_upload_page(self, test_client):
        """Test upload page returns 200."""
        response = test_client.get("/upload")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_pdfs_page(self, test_client, mock_db):
        """Test PDFs listing page."""
        mock_db.get_all_pdfs.return_value = [
            {"id": 1, "filename": "test.pdf", "num_pages": 5}
        ]
        
        response = test_client.get("/pdfs")
        assert response.status_code == 200
        mock_db.get_all_pdfs.assert_called_once()
    
    def test_pdf_detail_page_found(self, test_client, mock_db):
        """Test PDF detail page with existing PDF."""
        mock_db.get_pdf_by_id.return_value = {
            "id": 1, 
            "filename": "test.pdf",
            "num_pages": 5
        }
        mock_db.get_images_by_pdf_id.return_value = []
        mock_db.get_text_by_pdf_id.return_value = None
        
        response = test_client.get("/pdf/1")
        assert response.status_code == 200
        mock_db.get_pdf_by_id.assert_called_once_with(1)
    
    def test_pdf_detail_page_not_found(self, test_client, mock_db):
        """Test PDF detail page with non-existing PDF."""
        mock_db.get_pdf_by_id.return_value = None
        
        response = test_client.get("/pdf/999")
        assert response.status_code == 404
    
    def test_stats_page(self, test_client, mock_db, mock_embeddings_manager):
        """Test statistics page."""
        mock_db.get_all_pdfs.return_value = [
            {"id": 1, "num_pages": 5, "total_words": 1000, "total_images": 3}
        ]
        mock_db.get_pdfs_with_embeddings.return_value = []
        mock_embeddings_manager.get_collection_stats.return_value = {
            "total_embeddings": 0,
            "total_pdfs_with_embeddings": 0,
            "model_name": "test-model"
        }
        
        response = test_client.get("/stats")
        assert response.status_code == 200
    
    def test_process_page(self, test_client):
        """Test process page."""
        with patch('web_api.FileManager') as mock_fm:
            mock_fm.return_value.get_pdf_files.return_value = []
            response = test_client.get("/process")
            assert response.status_code == 200
    
    def test_embeddings_page(self, test_client, mock_db, mock_embeddings_manager):
        """Test embeddings management page."""
        mock_db.get_pdfs_with_embeddings.return_value = []
        mock_db.get_pdfs_without_embeddings.return_value = []
        mock_embeddings_manager.get_collection_stats.return_value = {
            "total_embeddings": 0
        }
        
        response = test_client.get("/embeddings")
        assert response.status_code == 200
    
    def test_search_page(self, test_client, mock_db):
        """Test search page."""
        mock_db.get_pdfs_with_embeddings.return_value = []
        
        response = test_client.get("/search")
        assert response.status_code == 200


class TestAPIEndpoints:
    """Tests for API endpoints."""
    
    def test_get_pdfs(self, test_client, mock_db):
        """Test GET /api/pdfs endpoint."""
        expected_pdfs = [
            {"id": 1, "filename": "test1.pdf"},
            {"id": 2, "filename": "test2.pdf"}
        ]
        mock_db.get_all_pdfs.return_value = expected_pdfs
        
        response = test_client.get("/api/pdfs")
        assert response.status_code == 200
        assert response.json() == expected_pdfs
    
    def test_get_pdf_by_id_found(self, test_client, mock_db):
        """Test GET /api/pdf/{pdf_id} with existing PDF."""
        mock_db.get_pdf_by_id.return_value = {
            "id": 1,
            "filename": "test.pdf"
        }
        mock_db.get_images_by_pdf_id.return_value = []
        mock_db.get_text_by_pdf_id.return_value = None
        
        response = test_client.get("/api/pdf/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "images" in data
        assert "text" in data
    
    def test_get_pdf_by_id_not_found(self, test_client, mock_db):
        """Test GET /api/pdf/{pdf_id} with non-existing PDF."""
        mock_db.get_pdf_by_id.return_value = None
        
        response = test_client.get("/api/pdf/999")
        assert response.status_code == 404
    
    def test_get_pdf_by_filename_found(self, test_client, mock_db):
        """Test GET /api/pdf/by-filename/{filename}."""
        mock_db.get_pdf_by_filename.return_value = {
            "id": 1,
            "filename": "test.pdf"
        }
        mock_db.get_images_by_pdf_id.return_value = []
        mock_db.get_text_by_pdf_id.return_value = None
        
        response = test_client.get("/api/pdf/by-filename/test.pdf")
        assert response.status_code == 200
        assert response.json()["filename"] == "test.pdf"
    
    def test_get_stats_empty(self, test_client, mock_db):
        """Test GET /api/stats with no PDFs."""
        mock_db.get_all_pdfs.return_value = []
        
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_pdfs"] == 0
        assert data["total_pages"] == 0
    
    def test_get_stats_with_data(self, test_client, mock_db):
        """Test GET /api/stats with PDF data."""
        mock_db.get_all_pdfs.return_value = [
            {"num_pages": 10, "total_words": 1000, "total_images": 5},
            {"num_pages": 20, "total_words": 2000, "total_images": 3}
        ]
        
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_pdfs"] == 2
        assert data["total_pages"] == 30
        assert data["total_words"] == 3000
        assert data["total_images"] == 8
        assert data["avg_pages"] == 15.0
        assert data["avg_words"] == 1500.0
    
    def test_get_pending_files(self, test_client):
        """Test GET /api/pending endpoint."""
        with patch('web_api.FileManager') as mock_fm:
            mock_fm.return_value.get_pdf_files.return_value = [
                Path("test1.pdf"),
                Path("test2.pdf")
            ]
            
            response = test_client.get("/api/pending")
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 2
            assert "test1.pdf" in data["files"]


class TestFileUpload:
    """Tests for file upload functionality."""
    
    def test_upload_single_pdf(self, test_client):
        """Test uploading a single PDF file."""
        files = {"files": ("test.pdf", b"fake pdf content", "application/pdf")}
        
        response = test_client.post("/api/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["uploaded"] == 1
        assert "test.pdf" in data["files"]
    
    def test_upload_multiple_pdfs(self, test_client):
        """Test uploading multiple PDF files."""
        files = [
            ("files", ("test1.pdf", b"fake pdf content 1", "application/pdf")),
            ("files", ("test2.pdf", b"fake pdf content 2", "application/pdf"))
        ]
        
        response = test_client.post("/api/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["uploaded"] == 2
    
    def test_upload_non_pdf_rejected(self, test_client):
        """Test that non-PDF files are rejected."""
        files = {"files": ("test.txt", b"text content", "text/plain")}
        
        response = test_client.post("/api/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["uploaded"] == 0
        assert data["errors"] is not None
    
    def test_upload_no_files(self, test_client):
        """Test upload endpoint with no files."""
        response = test_client.post("/api/upload")
        assert response.status_code == 422  # Validation error


class TestProcessing:
    """Tests for PDF processing functionality."""
    
    def test_process_pdfs_empty(self, test_client, mock_db):
        """Test processing with no pending files."""
        with patch('web_api.FileManager') as mock_fm:
            mock_fm.return_value.get_pdf_files.return_value = []
            
            response = test_client.post("/api/process")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["processed"] == 0


class TestEmbeddingsAPI:
    """Tests for embeddings API endpoints."""
    
    def test_generate_embeddings_success(self, test_client, mock_db, mock_embeddings_manager):
        """Test generating embeddings for a PDF."""
        mock_db.get_pdf_by_id.return_value = {
            "id": 1,
            "filename": "test.pdf"
        }
        mock_db.get_text_by_pdf_id.return_value = {
            "filename": "test_text.txt"
        }
        mock_embeddings_manager.add_pdf_embeddings.return_value = 10
        
        with patch('web_api.config') as mock_config:
            temp_dir = Path(tempfile.mkdtemp())
            mock_config.TEXT_DIR = temp_dir
            text_file = temp_dir / "test_text.txt"
            text_file.write_text("Sample text content")
            
            try:
                response = test_client.post("/api/embeddings/generate/1")
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["embeddings_count"] == 10
            finally:
                shutil.rmtree(temp_dir)
    
    def test_generate_embeddings_pdf_not_found(self, test_client, mock_db):
        """Test generating embeddings for non-existing PDF."""
        mock_db.get_pdf_by_id.return_value = None
        
        response = test_client.post("/api/embeddings/generate/999")
        assert response.status_code == 404
    
    def test_generate_embeddings_no_text(self, test_client, mock_db):
        """Test generating embeddings when no text extracted."""
        mock_db.get_pdf_by_id.return_value = {"id": 1, "filename": "test.pdf"}
        mock_db.get_text_by_pdf_id.return_value = None
        
        response = test_client.post("/api/embeddings/generate/1")
        assert response.status_code == 400
    
    def test_delete_embeddings(self, test_client, mock_embeddings_manager, mock_db):
        """Test deleting embeddings for a PDF."""
        mock_embeddings_manager.delete_pdf_embeddings.return_value = 5
        
        response = test_client.delete("/api/embeddings/1")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] == 5
        mock_db.clear_embeddings_status.assert_called_once_with(1)
    
    def test_get_embeddings_stats(self, test_client, mock_db, mock_embeddings_manager):
        """Test getting embeddings statistics."""
        mock_embeddings_manager.get_collection_stats.return_value = {
            "total_embeddings": 100,
            "model_name": "test-model"
        }
        mock_db.get_pdfs_with_embeddings.return_value = [{"id": 1}, {"id": 2}]
        mock_db.get_pdfs_without_embeddings.return_value = [{"id": 3}]
        
        response = test_client.get("/api/embeddings/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["collection_stats"]["total_embeddings"] == 100
        assert data["pdfs_with_embeddings"] == 2
        assert data["pdfs_without_embeddings"] == 1
    
    def test_search_embeddings(self, test_client, mock_db, mock_embeddings_manager):
        """Test semantic search endpoint."""
        mock_embeddings_manager.search_embeddings.return_value = {
            "results": [
                {
                    "document": "test content",
                    "distance": 0.5,
                    "metadata": {"pdf_id": 1, "chunk_index": 0}
                }
            ],
            "query": "test query"
        }
        mock_db.get_pdf_by_id.return_value = {
            "id": 1,
            "filename": "test.pdf",
            "title": "Test PDF"
        }
        
        response = test_client.post("/api/search", json={"query": "test query"})
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert "pdf_info" in data["results"][0]
    
    def test_search_embeddings_no_query(self, test_client):
        """Test search endpoint without query."""
        response = test_client.post("/api/search", json={})
        assert response.status_code == 400


class TestFileDownload:
    """Tests for file download endpoints."""
    
    def test_download_pdf_from_processed(self, test_client):
        """Test downloading PDF from processed directory."""
        with patch('web_api.config') as mock_config:
            temp_dir = Path(tempfile.mkdtemp())
            mock_config.PROCESSED_DIR = temp_dir
            mock_config.PENDING_DIR = temp_dir / "pending"
            
            # Create test PDF
            pdf_file = temp_dir / "test.pdf"
            pdf_file.write_bytes(b"fake pdf content")
            
            try:
                response = test_client.get("/api/download-pdf/test.pdf")
                assert response.status_code == 200
                assert response.headers["content-type"] == "application/pdf"
            finally:
                shutil.rmtree(temp_dir)
    
    def test_download_pdf_not_found(self, test_client):
        """Test downloading non-existing PDF."""
        with patch('web_api.config') as mock_config:
            temp_dir = Path(tempfile.mkdtemp())
            mock_config.PROCESSED_DIR = temp_dir
            mock_config.PENDING_DIR = temp_dir
            
            try:
                response = test_client.get("/api/download-pdf/nonexistent.pdf")
                assert response.status_code == 404
            finally:
                shutil.rmtree(temp_dir)

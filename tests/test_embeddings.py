"""
Tests for embeddings module.
"""
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys


@pytest.fixture
def temp_chroma_dir():
    """Create temporary directory for ChromaDB."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def embeddings_manager(temp_chroma_dir):
    """Create an EmbeddingsManager instance for testing."""
    from embeddings import EmbeddingsManager
    
    # Use a lightweight model for testing
    manager = EmbeddingsManager(
        persist_directory=str(temp_chroma_dir),
        model_name="all-MiniLM-L6-v2",
        chunk_size=100,
        chunk_overlap=10
    )
    return manager


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    This is a sample PDF document for testing purposes.
    It contains multiple paragraphs and sentences.
    
    The second paragraph has some more information.
    This will be used to test text chunking and embedding generation.
    
    A third paragraph to ensure we have enough content.
    Testing is important for maintaining code quality.
    """


class TestEmbeddingsManagerInit:
    """Tests for EmbeddingsManager initialization."""
    
    def test_initialization(self, embeddings_manager, temp_chroma_dir):
        """Test that EmbeddingsManager initializes correctly."""
        assert embeddings_manager is not None
        assert embeddings_manager.model_name == "all-MiniLM-L6-v2"
        assert embeddings_manager.persist_directory == temp_chroma_dir
        assert embeddings_manager.collection is not None
        assert embeddings_manager.model is not None
    
    def test_creates_persist_directory(self):
        """Test that persist directory is created if it doesn't exist."""
        from embeddings import EmbeddingsManager
        
        temp_dir = Path(tempfile.mkdtemp())
        chroma_dir = temp_dir / "new_chroma_db"
        
        try:
            assert not chroma_dir.exists()
            manager = EmbeddingsManager(persist_directory=str(chroma_dir))
            assert chroma_dir.exists()
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def test_custom_chunk_settings(self, temp_chroma_dir):
        """Test initialization with custom chunk settings."""
        from embeddings import EmbeddingsManager
        
        manager = EmbeddingsManager(
            persist_directory=str(temp_chroma_dir),
            chunk_size=200,
            chunk_overlap=20
        )
        
        assert manager.text_splitter._chunk_size == 200
        assert manager.text_splitter._chunk_overlap == 20


class TestTextChunking:
    """Tests for text chunking functionality."""
    
    def test_chunk_text_basic(self, embeddings_manager, sample_text):
        """Test basic text chunking."""
        chunks = embeddings_manager.chunk_text(sample_text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
    
    def test_chunk_text_respects_size(self, embeddings_manager):
        """Test that chunks respect the configured size."""
        long_text = "word " * 500  # Create long text
        chunks = embeddings_manager.chunk_text(long_text)
        
        # Most chunks should be close to the chunk size
        for chunk in chunks[:-1]:  # Exclude last chunk which may be shorter
            assert len(chunk) <= embeddings_manager.text_splitter._chunk_size + 50
    
    def test_chunk_text_empty_string(self, embeddings_manager):
        """Test chunking empty string."""
        chunks = embeddings_manager.chunk_text("")
        assert chunks == []
    
    def test_chunk_text_whitespace_only(self, embeddings_manager):
        """Test chunking whitespace-only string."""
        chunks = embeddings_manager.chunk_text("   \n\n  \t  ")
        assert chunks == []
    
    def test_chunk_text_short_text(self, embeddings_manager):
        """Test chunking text shorter than chunk size."""
        short_text = "This is a short sentence."
        chunks = embeddings_manager.chunk_text(short_text)
        
        assert len(chunks) == 1
        assert chunks[0] == short_text


class TestEmbeddingGeneration:
    """Tests for embedding generation."""
    
    def test_generate_embeddings_basic(self, embeddings_manager):
        """Test basic embedding generation."""
        texts = ["This is a test sentence.", "Another test sentence."]
        embeddings = embeddings_manager.generate_embeddings(texts)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == 2
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)
        # Check that embeddings are numeric
        assert all(isinstance(val, float) for emb in embeddings for val in emb)
    
    def test_generate_embeddings_empty_list(self, embeddings_manager):
        """Test generating embeddings for empty list."""
        embeddings = embeddings_manager.generate_embeddings([])
        assert embeddings == []
    
    def test_generate_embeddings_single_text(self, embeddings_manager):
        """Test generating embedding for single text."""
        texts = ["Single sentence."]
        embeddings = embeddings_manager.generate_embeddings(texts)
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) > 0
    
    def test_embeddings_dimension_consistency(self, embeddings_manager):
        """Test that all embeddings have the same dimension."""
        texts = ["First text.", "Second text.", "Third text."]
        embeddings = embeddings_manager.generate_embeddings(texts)
        
        dimensions = [len(emb) for emb in embeddings]
        assert len(set(dimensions)) == 1  # All should have same dimension


class TestPDFEmbeddings:
    """Tests for PDF-specific embedding operations."""
    
    def test_add_pdf_embeddings(self, embeddings_manager, sample_text):
        """Test adding embeddings for a PDF."""
        count = embeddings_manager.add_pdf_embeddings(
            pdf_id=1,
            pdf_filename="test.pdf",
            text=sample_text
        )
        
        assert count > 0
        assert isinstance(count, int)
    
    def test_add_pdf_embeddings_metadata(self, embeddings_manager, sample_text):
        """Test that PDF embeddings are stored with correct metadata."""
        count = embeddings_manager.add_pdf_embeddings(
            pdf_id=1,
            pdf_filename="test.pdf",
            text=sample_text
        )
        
        # Query the collection to verify metadata
        results = embeddings_manager.collection.get(
            ids=[f"pdf_1_chunk_0"]
        )
        
        assert len(results['ids']) == 1
        assert results['metadatas'][0]['pdf_id'] == 1
        assert results['metadatas'][0]['pdf_filename'] == "test.pdf"
        assert results['metadatas'][0]['chunk_index'] == 0
        assert 'chunk_size' in results['metadatas'][0]
    
    def test_add_pdf_embeddings_empty_text(self, embeddings_manager):
        """Test adding embeddings with empty text."""
        count = embeddings_manager.add_pdf_embeddings(
            pdf_id=1,
            pdf_filename="test.pdf",
            text=""
        )
        
        assert count == 0
    
    def test_add_multiple_pdfs(self, embeddings_manager, sample_text):
        """Test adding embeddings for multiple PDFs."""
        count1 = embeddings_manager.add_pdf_embeddings(1, "test1.pdf", sample_text)
        count2 = embeddings_manager.add_pdf_embeddings(2, "test2.pdf", sample_text)
        
        assert count1 > 0
        assert count2 > 0
        
        # Verify both PDFs are in collection
        all_items = embeddings_manager.collection.get()
        pdf_ids = set(meta['pdf_id'] for meta in all_items['metadatas'])
        assert 1 in pdf_ids
        assert 2 in pdf_ids
    
    def test_delete_pdf_embeddings(self, embeddings_manager, sample_text):
        """Test deleting embeddings for a PDF."""
        # First add embeddings
        count_added = embeddings_manager.add_pdf_embeddings(
            pdf_id=1,
            pdf_filename="test.pdf",
            text=sample_text
        )
        
        # Then delete them
        count_deleted = embeddings_manager.delete_pdf_embeddings(pdf_id=1)
        
        assert count_deleted == count_added
        
        # Verify they're deleted
        results = embeddings_manager.collection.get(
            where={"pdf_id": 1}
        )
        assert len(results['ids']) == 0
    
    def test_delete_nonexistent_pdf_embeddings(self, embeddings_manager):
        """Test deleting embeddings for non-existing PDF."""
        count = embeddings_manager.delete_pdf_embeddings(pdf_id=999)
        assert count == 0
    
    def test_delete_specific_pdf_only(self, embeddings_manager, sample_text):
        """Test that deleting one PDF doesn't affect others."""
        # Add embeddings for two PDFs
        embeddings_manager.add_pdf_embeddings(1, "test1.pdf", sample_text)
        embeddings_manager.add_pdf_embeddings(2, "test2.pdf", sample_text)
        
        # Delete first PDF
        embeddings_manager.delete_pdf_embeddings(1)
        
        # Verify second PDF still has embeddings
        results = embeddings_manager.collection.get(
            where={"pdf_id": 2}
        )
        assert len(results['ids']) > 0


class TestSemanticSearch:
    """Tests for semantic search functionality."""
    
    def test_search_embeddings_basic(self, embeddings_manager):
        """Test basic semantic search."""
        # Add some test data
        texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Python is a popular programming language.",
            "Deep learning uses neural networks."
        ]
        for i, text in enumerate(texts):
            embeddings_manager.add_pdf_embeddings(
                pdf_id=i+1,
                pdf_filename=f"test{i+1}.pdf",
                text=text
            )
        
        # Search
        results = embeddings_manager.search_embeddings(
            query="artificial intelligence",
            n_results=2
        )
        
        assert 'results' in results
        assert len(results['results']) <= 2
        assert 'query' in results
    
    def test_search_embeddings_with_pdf_filter(self, embeddings_manager, sample_text):
        """Test searching with PDF ID filter."""
        # Add embeddings for multiple PDFs
        embeddings_manager.add_pdf_embeddings(1, "test1.pdf", sample_text)
        embeddings_manager.add_pdf_embeddings(2, "test2.pdf", sample_text)
        
        # Search with filter
        results = embeddings_manager.search_embeddings(
            query="testing",
            n_results=5,
            pdf_id=1
        )
        
        # All results should be from PDF 1
        assert all(r['metadata']['pdf_id'] == 1 for r in results['results'])
    
    def test_search_embeddings_empty_collection(self, embeddings_manager):
        """Test searching in empty collection."""
        results = embeddings_manager.search_embeddings(
            query="test query",
            n_results=5
        )
        
        assert results['results'] == []
    
    def test_search_embeddings_result_structure(self, embeddings_manager, sample_text):
        """Test that search results have correct structure."""
        embeddings_manager.add_pdf_embeddings(1, "test.pdf", sample_text)
        
        results = embeddings_manager.search_embeddings(
            query="testing",
            n_results=3
        )
        
        assert 'results' in results
        assert 'query' in results
        
        for result in results['results']:
            assert 'document' in result
            assert 'distance' in result
            assert 'metadata' in result
            assert 'pdf_id' in result['metadata']
            assert 'pdf_filename' in result['metadata']
            assert 'chunk_index' in result['metadata']
    
    def test_search_respects_n_results(self, embeddings_manager, sample_text):
        """Test that search returns requested number of results."""
        embeddings_manager.add_pdf_embeddings(1, "test.pdf", sample_text * 3)
        
        for n in [1, 3, 5]:
            results = embeddings_manager.search_embeddings(
                query="testing",
                n_results=n
            )
            assert len(results['results']) <= n


class TestCollectionStats:
    """Tests for collection statistics."""
    
    def test_get_collection_stats_empty(self, embeddings_manager):
        """Test getting stats from empty collection."""
        stats = embeddings_manager.get_collection_stats()
        
        assert 'total_embeddings' in stats
        assert stats['total_embeddings'] == 0
        assert 'model_name' in stats
        assert stats['model_name'] == "all-MiniLM-L6-v2"
    
    def test_get_collection_stats_with_data(self, embeddings_manager, sample_text):
        """Test getting stats after adding embeddings."""
        count = embeddings_manager.add_pdf_embeddings(1, "test.pdf", sample_text)
        
        stats = embeddings_manager.get_collection_stats()
        
        assert stats['total_embeddings'] == count
        assert stats['total_pdfs_with_embeddings'] == 1
        assert 'model_name' in stats
    
    def test_get_collection_stats_multiple_pdfs(self, embeddings_manager, sample_text):
        """Test stats with multiple PDFs."""
        embeddings_manager.add_pdf_embeddings(1, "test1.pdf", sample_text)
        embeddings_manager.add_pdf_embeddings(2, "test2.pdf", sample_text)
        embeddings_manager.add_pdf_embeddings(3, "test3.pdf", sample_text)
        
        stats = embeddings_manager.get_collection_stats()
        
        assert stats['total_embeddings'] > 0
        assert stats['total_pdfs_with_embeddings'] == 3


class TestPersistence:
    """Tests for data persistence."""
    
    def test_persistence_across_instances(self, temp_chroma_dir, sample_text):
        """Test that data persists across manager instances."""
        from embeddings import EmbeddingsManager
        
        # Create first instance and add data
        manager1 = EmbeddingsManager(persist_directory=str(temp_chroma_dir))
        count = manager1.add_pdf_embeddings(1, "test.pdf", sample_text)
        
        # Create second instance
        manager2 = EmbeddingsManager(persist_directory=str(temp_chroma_dir))
        
        # Verify data persists
        stats = manager2.get_collection_stats()
        assert stats['total_embeddings'] == count
    
    def test_delete_persists(self, temp_chroma_dir, sample_text):
        """Test that deletions persist."""
        from embeddings import EmbeddingsManager
        
        # Create first instance, add and delete data
        manager1 = EmbeddingsManager(persist_directory=str(temp_chroma_dir))
        manager1.add_pdf_embeddings(1, "test.pdf", sample_text)
        manager1.delete_pdf_embeddings(1)
        
        # Create second instance
        manager2 = EmbeddingsManager(persist_directory=str(temp_chroma_dir))
        
        # Verify deletion persists
        stats = manager2.get_collection_stats()
        assert stats['total_embeddings'] == 0


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_handle_invalid_pdf_id_type(self, embeddings_manager, sample_text):
        """Test handling invalid PDF ID type."""
        # Should handle gracefully or raise appropriate error
        try:
            embeddings_manager.add_pdf_embeddings(
                pdf_id="invalid",
                pdf_filename="test.pdf",
                text=sample_text
            )
        except (TypeError, ValueError):
            pass  # Expected error
    
    def test_handle_none_text(self, embeddings_manager):
        """Test handling None as text."""
        # Should handle gracefully
        count = embeddings_manager.add_pdf_embeddings(
            pdf_id=1,
            pdf_filename="test.pdf",
            text=None
        )
        assert count == 0

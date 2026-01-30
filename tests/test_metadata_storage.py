"""
Tests for metadata_storage module.
"""
import pytest
from pathlib import Path
import tempfile
import shutil
import json
from datetime import datetime


@pytest.fixture
def temp_storage_dir():
    """Create temporary directory for storage file."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def storage_file(temp_storage_dir):
    """Create a storage file path."""
    return temp_storage_dir / "metadata.json"


@pytest.fixture
def metadata_storage(storage_file):
    """Create a MetadataStorage instance."""
    from metadata_storage import MetadataStorage
    return MetadataStorage(storage_file)


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return {
        "title": "Test Document",
        "author": "Test Author",
        "num_pages": 10,
        "total_words": 1000
    }


class TestMetadataStorageInit:
    """Tests for MetadataStorage initialization."""
    
    def test_initialization_creates_file(self, storage_file):
        """Test that initialization creates storage file."""
        from metadata_storage import MetadataStorage
        
        assert not storage_file.exists()
        
        storage = MetadataStorage(storage_file)
        
        assert storage_file.exists()
        with open(storage_file, 'r') as f:
            data = json.load(f)
        assert data == {}
    
    def test_initialization_creates_parent_directories(self, temp_storage_dir):
        """Test that parent directories are created if needed."""
        from metadata_storage import MetadataStorage
        
        nested_path = temp_storage_dir / "deep" / "nested" / "path" / "metadata.json"
        assert not nested_path.parent.exists()
        
        storage = MetadataStorage(nested_path)
        
        assert nested_path.exists()
        assert nested_path.parent.exists()
    
    def test_initialization_with_existing_file(self, storage_file):
        """Test initialization with existing storage file."""
        from metadata_storage import MetadataStorage
        
        # Create file with existing data
        existing_data = {"test.pdf": {"title": "Existing"}}
        with open(storage_file, 'w') as f:
            json.dump(existing_data, f)
        
        storage = MetadataStorage(storage_file)
        
        # Should load existing data
        data = storage.get_all_metadata()
        assert data == existing_data


class TestFileExists:
    """Tests for file_exists method."""
    
    def test_file_exists_true(self, metadata_storage, sample_metadata):
        """Test checking for existing file."""
        metadata_storage.add_metadata("test.pdf", sample_metadata)
        
        assert metadata_storage.file_exists("test.pdf") is True
    
    def test_file_exists_false(self, metadata_storage):
        """Test checking for non-existing file."""
        assert metadata_storage.file_exists("nonexistent.pdf") is False
    
    def test_file_exists_empty_storage(self, metadata_storage):
        """Test file_exists on empty storage."""
        assert metadata_storage.file_exists("any.pdf") is False


class TestAddMetadata:
    """Tests for add_metadata method."""
    
    def test_add_metadata_new_file(self, metadata_storage, sample_metadata):
        """Test adding metadata for new file."""
        result = metadata_storage.add_metadata("test.pdf", sample_metadata)
        
        assert result is True
        assert metadata_storage.file_exists("test.pdf")
        
        stored = metadata_storage.get_metadata("test.pdf")
        assert stored["title"] == sample_metadata["title"]
        assert stored["author"] == sample_metadata["author"]
        assert "processed_at" in stored
    
    def test_add_metadata_updates_existing(self, metadata_storage, sample_metadata):
        """Test that adding metadata for existing file updates it."""
        # Add initial metadata
        metadata_storage.add_metadata("test.pdf", sample_metadata)
        
        # Update with new metadata
        new_metadata = {"title": "Updated Title", "author": "New Author"}
        result = metadata_storage.add_metadata("test.pdf", new_metadata)
        
        assert result is True
        stored = metadata_storage.get_metadata("test.pdf")
        assert stored["title"] == "Updated Title"
        assert stored["author"] == "New Author"
    
    def test_add_metadata_adds_timestamp(self, metadata_storage, sample_metadata):
        """Test that processed_at timestamp is added."""
        before = datetime.now()
        metadata_storage.add_metadata("test.pdf", sample_metadata)
        after = datetime.now()
        
        stored = metadata_storage.get_metadata("test.pdf")
        assert "processed_at" in stored
        
        # Verify timestamp is valid
        timestamp = datetime.fromisoformat(stored["processed_at"])
        assert before <= timestamp <= after
    
    def test_add_metadata_multiple_files(self, metadata_storage):
        """Test adding metadata for multiple files."""
        files = {
            "file1.pdf": {"title": "File 1"},
            "file2.pdf": {"title": "File 2"},
            "file3.pdf": {"title": "File 3"}
        }
        
        for filename, metadata in files.items():
            result = metadata_storage.add_metadata(filename, metadata)
            assert result is True
        
        # Verify all were added
        for filename in files.keys():
            assert metadata_storage.file_exists(filename)
    
    def test_add_metadata_empty_dict(self, metadata_storage):
        """Test adding empty metadata dict."""
        result = metadata_storage.add_metadata("test.pdf", {})
        
        assert result is True
        stored = metadata_storage.get_metadata("test.pdf")
        assert "processed_at" in stored  # Should still add timestamp


class TestGetMetadata:
    """Tests for get_metadata method."""
    
    def test_get_metadata_existing_file(self, metadata_storage, sample_metadata):
        """Test getting metadata for existing file."""
        metadata_storage.add_metadata("test.pdf", sample_metadata)
        
        retrieved = metadata_storage.get_metadata("test.pdf")
        
        assert retrieved is not None
        assert retrieved["title"] == sample_metadata["title"]
        assert retrieved["author"] == sample_metadata["author"]
    
    def test_get_metadata_nonexistent_file(self, metadata_storage):
        """Test getting metadata for non-existing file."""
        retrieved = metadata_storage.get_metadata("nonexistent.pdf")
        
        assert retrieved is None
    
    def test_get_metadata_empty_storage(self, metadata_storage):
        """Test getting metadata from empty storage."""
        retrieved = metadata_storage.get_metadata("any.pdf")
        
        assert retrieved is None


class TestGetAllMetadata:
    """Tests for get_all_metadata method."""
    
    def test_get_all_metadata_empty(self, metadata_storage):
        """Test getting all metadata when empty."""
        data = metadata_storage.get_all_metadata()
        
        assert data == {}
    
    def test_get_all_metadata_with_data(self, metadata_storage):
        """Test getting all metadata with files."""
        files = {
            "file1.pdf": {"title": "File 1"},
            "file2.pdf": {"title": "File 2"}
        }
        
        for filename, metadata in files.items():
            metadata_storage.add_metadata(filename, metadata)
        
        all_data = metadata_storage.get_all_metadata()
        
        assert len(all_data) == 2
        assert "file1.pdf" in all_data
        assert "file2.pdf" in all_data
    
    def test_get_all_metadata_returns_copy(self, metadata_storage, sample_metadata):
        """Test that get_all_metadata returns data correctly."""
        metadata_storage.add_metadata("test.pdf", sample_metadata)
        
        data1 = metadata_storage.get_all_metadata()
        data2 = metadata_storage.get_all_metadata()
        
        # Both should have same content
        assert data1 == data2


class TestRemoveMetadata:
    """Tests for remove_metadata method."""
    
    def test_remove_metadata_existing_file(self, metadata_storage, sample_metadata):
        """Test removing metadata for existing file."""
        metadata_storage.add_metadata("test.pdf", sample_metadata)
        
        result = metadata_storage.remove_metadata("test.pdf")
        
        assert result is True
        assert not metadata_storage.file_exists("test.pdf")
    
    def test_remove_metadata_nonexistent_file(self, metadata_storage):
        """Test removing metadata for non-existing file."""
        result = metadata_storage.remove_metadata("nonexistent.pdf")
        
        assert result is False
    
    def test_remove_metadata_preserves_others(self, metadata_storage):
        """Test that removing one file doesn't affect others."""
        metadata_storage.add_metadata("file1.pdf", {"title": "File 1"})
        metadata_storage.add_metadata("file2.pdf", {"title": "File 2"})
        metadata_storage.add_metadata("file3.pdf", {"title": "File 3"})
        
        metadata_storage.remove_metadata("file2.pdf")
        
        assert metadata_storage.file_exists("file1.pdf")
        assert not metadata_storage.file_exists("file2.pdf")
        assert metadata_storage.file_exists("file3.pdf")


class TestGetProcessedFiles:
    """Tests for get_processed_files method."""
    
    def test_get_processed_files_empty(self, metadata_storage):
        """Test getting processed files when empty."""
        files = metadata_storage.get_processed_files()
        
        assert files == []
    
    def test_get_processed_files_with_data(self, metadata_storage):
        """Test getting list of processed files."""
        filenames = ["file1.pdf", "file2.pdf", "file3.pdf"]
        
        for filename in filenames:
            metadata_storage.add_metadata(filename, {"title": "Test"})
        
        processed = metadata_storage.get_processed_files()
        
        assert len(processed) == 3
        for filename in filenames:
            assert filename in processed


class TestGetCount:
    """Tests for get_count method."""
    
    def test_get_count_empty(self, metadata_storage):
        """Test count with empty storage."""
        count = metadata_storage.get_count()
        
        assert count == 0
    
    def test_get_count_with_files(self, metadata_storage):
        """Test count with files."""
        for i in range(5):
            metadata_storage.add_metadata(f"file{i}.pdf", {"title": f"File {i}"})
        
        count = metadata_storage.get_count()
        
        assert count == 5
    
    def test_get_count_after_removal(self, metadata_storage):
        """Test count after removing files."""
        metadata_storage.add_metadata("file1.pdf", {"title": "File 1"})
        metadata_storage.add_metadata("file2.pdf", {"title": "File 2"})
        metadata_storage.add_metadata("file3.pdf", {"title": "File 3"})
        
        assert metadata_storage.get_count() == 3
        
        metadata_storage.remove_metadata("file2.pdf")
        
        assert metadata_storage.get_count() == 2


class TestMigration:
    """Tests for migration from old array format."""
    
    def test_migrate_from_array_format(self, storage_file):
        """Test automatic migration from old array format."""
        from metadata_storage import MetadataStorage
        
        # Create file with old array format
        old_format = [
            {"file1.pdf": {"title": "File 1"}},
            {"file2.pdf": {"title": "File 2"}}
        ]
        with open(storage_file, 'w') as f:
            json.dump(old_format, f)
        
        # Initialize storage (should trigger migration)
        storage = MetadataStorage(storage_file)
        
        # Verify data was migrated to dict format
        data = storage.get_all_metadata()
        assert isinstance(data, dict)
        assert "file1.pdf" in data
        assert "file2.pdf" in data
        assert data["file1.pdf"]["title"] == "File 1"
    
    def test_migrate_handles_duplicates(self, storage_file):
        """Test migration handles duplicate entries."""
        from metadata_storage import MetadataStorage
        
        # Create file with duplicates (last should win)
        old_format = [
            {"test.pdf": {"title": "First"}},
            {"other.pdf": {"title": "Other"}},
            {"test.pdf": {"title": "Last"}}  # Duplicate
        ]
        with open(storage_file, 'w') as f:
            json.dump(old_format, f)
        
        storage = MetadataStorage(storage_file)
        
        # Verify last entry is kept
        data = storage.get_all_metadata()
        assert data["test.pdf"]["title"] == "Last"
        assert len(data) == 2  # test.pdf and other.pdf
    
    def test_no_migration_needed_for_dict(self, storage_file):
        """Test that dict format doesn't trigger migration."""
        from metadata_storage import MetadataStorage
        
        # Create file with new dict format
        new_format = {
            "file1.pdf": {"title": "File 1"},
            "file2.pdf": {"title": "File 2"}
        }
        with open(storage_file, 'w') as f:
            json.dump(new_format, f)
        
        storage = MetadataStorage(storage_file)
        
        # Should load as-is
        data = storage.get_all_metadata()
        assert data == new_format


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_handle_corrupt_json(self, storage_file):
        """Test handling corrupt JSON file."""
        from metadata_storage import MetadataStorage
        
        # Create corrupt JSON file
        with open(storage_file, 'w') as f:
            f.write("not valid json{{{")
        
        # Should handle gracefully and return empty dict
        storage = MetadataStorage(storage_file)
        data = storage.get_all_metadata()
        
        assert data == {}
    
    def test_handle_invalid_json_structure(self, storage_file):
        """Test handling invalid JSON structure."""
        from metadata_storage import MetadataStorage
        
        # Create file with string instead of dict/list
        with open(storage_file, 'w') as f:
            json.dump("invalid", f)
        
        storage = MetadataStorage(storage_file)
        data = storage.get_all_metadata()
        
        assert data == {}


class TestPersistence:
    """Tests for data persistence."""
    
    def test_data_persists_across_instances(self, storage_file, sample_metadata):
        """Test that data persists when creating new instances."""
        from metadata_storage import MetadataStorage
        
        # Create first instance and add data
        storage1 = MetadataStorage(storage_file)
        storage1.add_metadata("test.pdf", sample_metadata)
        
        # Create second instance
        storage2 = MetadataStorage(storage_file)
        
        # Verify data persists
        assert storage2.file_exists("test.pdf")
        retrieved = storage2.get_metadata("test.pdf")
        assert retrieved["title"] == sample_metadata["title"]
    
    def test_changes_persist(self, storage_file):
        """Test that all changes persist."""
        from metadata_storage import MetadataStorage
        
        storage1 = MetadataStorage(storage_file)
        storage1.add_metadata("file1.pdf", {"title": "File 1"})
        storage1.add_metadata("file2.pdf", {"title": "File 2"})
        storage1.remove_metadata("file1.pdf")
        
        # Create new instance and verify changes
        storage2 = MetadataStorage(storage_file)
        assert not storage2.file_exists("file1.pdf")
        assert storage2.file_exists("file2.pdf")
        assert storage2.get_count() == 1


class TestDeduplication:
    """Tests for deduplication functionality."""
    
    def test_prevents_duplicate_processing(self, metadata_storage, sample_metadata):
        """Test that file_exists can be used to prevent duplicates."""
        filename = "test.pdf"
        
        # First processing
        if not metadata_storage.file_exists(filename):
            metadata_storage.add_metadata(filename, sample_metadata)
        
        # Attempt second processing
        if not metadata_storage.file_exists(filename):
            pytest.fail("Should have detected file already exists")
        
        # Verify only one entry
        assert metadata_storage.get_count() == 1
    
    def test_allows_reprocessing_after_removal(self, metadata_storage, sample_metadata):
        """Test that files can be reprocessed after removal."""
        filename = "test.pdf"
        
        # First processing
        metadata_storage.add_metadata(filename, sample_metadata)
        
        # Remove
        metadata_storage.remove_metadata(filename)
        
        # Should be able to process again
        assert not metadata_storage.file_exists(filename)
        metadata_storage.add_metadata(filename, sample_metadata)
        
        assert metadata_storage.file_exists(filename)

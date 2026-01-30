"""
Metadata storage module for managing PDF metadata persistence.
Implements deduplication to prevent processing the same file multiple times.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class MetadataStorage:
    """Handle metadata storage and retrieval with deduplication support."""
    
    def __init__(self, storage_file):
        """
        Initialize metadata storage.
        
        Args:
            storage_file (str or Path): Path to the JSON storage file
        """
        self.storage_file = Path(storage_file)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the storage file if it doesn't exist."""
        if not self.storage_file.exists():
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_data({})
            logger.info(f"Created new metadata storage file: {self.storage_file}")
    
    def _load_data(self):
        """
        Load metadata from the storage file.
        
        Returns:
            dict: Metadata dictionary (filename -> metadata)
        """
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle migration from old array format to new dict format
                if isinstance(data, list):
                    logger.warning("Detected old array format. Migrating to dictionary format...")
                    migrated_data = self._migrate_from_array(data)
                    self._save_data(migrated_data)
                    return migrated_data
                
                return data if isinstance(data, dict) else {}
                
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {self.storage_file}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}
    
    def _save_data(self, data):
        """
        Save metadata to the storage file.
        
        Args:
            data (dict): Metadata dictionary to save
        """
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.debug(f"Saved metadata to {self.storage_file}")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _migrate_from_array(self, array_data):
        """
        Migrate from old array format to new dictionary format.
        Old format: [{"file1.pdf": {...}}, {"file2.pdf": {...}}]
        New format: {"file1.pdf": {...}, "file2.pdf": {...}}
        
        Args:
            array_data (list): Old format data
            
        Returns:
            dict: New format data with duplicates removed
        """
        migrated = {}
        for item in array_data:
            if isinstance(item, dict):
                for filename, metadata in item.items():
                    # Keep the last occurrence if duplicates exist
                    if filename in migrated:
                        logger.warning(f"Duplicate entry found for {filename} during migration. Keeping latest.")
                    migrated[filename] = metadata
        
        logger.info(f"Migrated {len(array_data)} entries to {len(migrated)} unique entries")
        return migrated
    
    def file_exists(self, filename):
        """
        Check if a file has already been processed.
        
        Args:
            filename (str): Name of the PDF file
            
        Returns:
            bool: True if file exists in metadata, False otherwise
        """
        data = self._load_data()
        return filename in data
    
    def add_metadata(self, filename, metadata):
        """
        Add or update metadata for a file.
        
        Args:
            filename (str): Name of the PDF file
            metadata (dict): Metadata dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data = self._load_data()
            
            # Add processing timestamp
            metadata['processed_at'] = datetime.now().isoformat()
            
            if filename in data:
                logger.info(f"Updating existing metadata for {filename}")
            else:
                logger.info(f"Adding new metadata for {filename}")
            
            data[filename] = metadata
            self._save_data(data)
            return True
            
        except Exception as e:
            logger.error(f"Error adding metadata for {filename}: {e}")
            return False
    
    def get_metadata(self, filename):
        """
        Get metadata for a specific file.
        
        Args:
            filename (str): Name of the PDF file
            
        Returns:
            dict or None: Metadata dictionary if found, None otherwise
        """
        data = self._load_data()
        return data.get(filename)
    
    def get_all_metadata(self):
        """
        Get all metadata.
        
        Returns:
            dict: Dictionary of all metadata (filename -> metadata)
        """
        return self._load_data()
    
    def remove_metadata(self, filename):
        """
        Remove metadata for a specific file.
        
        Args:
            filename (str): Name of the PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data = self._load_data()
            
            if filename in data:
                del data[filename]
                self._save_data(data)
                logger.info(f"Removed metadata for {filename}")
                return True
            else:
                logger.warning(f"No metadata found for {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing metadata for {filename}: {e}")
            return False
    
    def get_processed_files(self):
        """
        Get list of all processed file names.
        
        Returns:
            list: List of processed filenames
        """
        data = self._load_data()
        return list(data.keys())
    
    def get_count(self):
        """
        Get the count of processed files.
        
        Returns:
            int: Number of processed files
        """
        data = self._load_data()
        return len(data)

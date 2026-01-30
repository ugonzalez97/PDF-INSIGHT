"""
File management module for handling file system operations.
"""
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class FileManager:
    """Handle file system operations for PDF processing."""
    
    @staticmethod
    def get_pdf_files(folder_path):
        """
        Get all PDF files from a folder.
        
        Args:
            folder_path (str or Path): Path to the folder containing PDFs
            
        Returns:
            list: List of Path objects for PDF files
        """
        folder_path = Path(folder_path)
        
        if not folder_path.is_dir():
            logger.error(f"The folder path {folder_path} does not exist or is not a directory.")
            return []
        
        pdf_files = list(folder_path.glob("*.pdf")) + list(folder_path.glob("*.PDF"))
        logger.info(f"Found {len(pdf_files)} PDF files in {folder_path}")
        return pdf_files
    
    @staticmethod
    def move_file(source_path, dest_dir):
        """
        Move a file to a destination directory.
        
        Args:
            source_path (str or Path): Path to the source file
            dest_dir (str or Path): Destination directory
            
        Returns:
            Path or None: Path to the moved file if successful, None otherwise
        """
        try:
            source_path = Path(source_path)
            dest_dir = Path(dest_dir)
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            dest_path = dest_dir / source_path.name
            
            # Handle case where file already exists in destination
            if dest_path.exists():
                logger.warning(f"File {dest_path.name} already exists in {dest_dir}. Skipping move.")
                return dest_path
            
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"Moved {source_path.name} to {dest_dir}")
            return dest_path
            
        except Exception as e:
            logger.error(f"Error moving file {source_path}: {e}")
            return None
    
    @staticmethod
    def move_files_batch(source_dir, dest_dir, file_list=None):
        """
        Move multiple files from source directory to destination directory.
        
        Args:
            source_dir (str or Path): Source directory
            dest_dir (str or Path): Destination directory
            file_list (list, optional): List of filenames to move. If None, moves all files.
            
        Returns:
            int: Number of files successfully moved
        """
        source_dir = Path(source_dir)
        dest_dir = Path(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        moved_count = 0
        
        try:
            if file_list:
                files_to_move = [source_dir / filename for filename in file_list]
            else:
                files_to_move = [f for f in source_dir.iterdir() if f.is_file()]
            
            for file_path in files_to_move:
                if file_path.exists():
                    result = FileManager.move_file(file_path, dest_dir)
                    if result:
                        moved_count += 1
            
            logger.info(f"Moved {moved_count} files from {source_dir} to {dest_dir}")
            return moved_count
            
        except Exception as e:
            logger.error(f"Error during batch file move: {e}")
            return moved_count
    
    @staticmethod
    def ensure_directory(directory):
        """
        Ensure a directory exists, create it if it doesn't.
        
        Args:
            directory (str or Path): Directory path
            
        Returns:
            Path: Path object for the directory
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
        return directory
    
    @staticmethod
    def get_file_size(file_path):
        """
        Get the size of a file in bytes.
        
        Args:
            file_path (str or Path): Path to the file
            
        Returns:
            int or None: File size in bytes, or None if error
        """
        try:
            file_path = Path(file_path)
            return file_path.stat().st_size
        except Exception as e:
            logger.error(f"Error getting file size for {file_path}: {e}")
            return None
        
    @staticmethod
    def save_text_file(pdf_name, text_content, output_dir, hex_id):
        """
        Save extracted text content to a .txt file with hexadecimal identifier.
        
        Args:
            pdf_name (str): Name of the PDF file (without extension)
            text_content (str): Extracted text content
            output_dir (str or Path): Directory to save the text file
            hex_id (str): Hexadecimal identifier for uniqueness
            
        Returns:
            tuple: (filename, Path) if successful, (None, None) otherwise
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filename with hex ID
            text_filename = f"{pdf_name}_{hex_id}_text.txt"
            text_file_path = output_dir / text_filename
            
            with open(text_file_path, 'w', encoding='utf-8') as text_file:
                text_file.write(text_content)
            
            logger.info(f"Saved extracted text to {text_file_path}")
            return text_filename, text_file_path
            
        except Exception as e:
            logger.error(f"Error saving text file for {pdf_name}: {e}")
            return None, None

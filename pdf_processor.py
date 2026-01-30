"""
PDF processing module for extracting metadata and images from PDF files.
"""
import logging
from datetime import datetime
from pypdf import PdfReader
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handle PDF reading and metadata/image extraction."""
    
    def __init__(self):
        pass
    
    @staticmethod
    def open_pdf(file_path):
        """
        Open a PDF file and return a PdfReader object.
        
        Args:
            file_path (str or Path): Path to the PDF file
            
        Returns:
            PdfReader or None: PdfReader object if successful, None otherwise
        """
        try:
            reader = PdfReader(str(file_path))
            logger.info(f"Successfully opened PDF: {file_path}")
            return reader
        except Exception as e:
            logger.error(f"Error opening PDF file {file_path}: {e}")
            return None
    
    @staticmethod
    def get_basic_metadata(reader):
        """
        Extract basic metadata from a PdfReader object.
        
        Args:
            reader (PdfReader): PdfReader object
            
        Returns:
            dict: Basic metadata (title, author, dates, etc.)
        """
        metadata = reader.metadata
        
        def parse_date(date_str):
            """Convert date to ISO format string."""
            if isinstance(date_str, datetime):
                return date_str.isoformat()
            return date_str
        
        return {
            "title": metadata.title,
            "author": metadata.author,
            "subject": metadata.subject,
            "creator": metadata.creator,
            "producer": metadata.producer,
            "creation_date": parse_date(metadata.creation_date),
            "modification_date": parse_date(metadata.modification_date),
        }
    
    @staticmethod
    def get_num_pages(reader):
        """
        Get the number of pages in the PDF.
        
        Args:
            reader (PdfReader): PdfReader object
            
        Returns:
            int: Number of pages
        """
        return len(reader.pages)
    
    @staticmethod
    def get_total_words(reader):
        """
        Count the total number of words in the PDF.
        
        Args:
            reader (PdfReader): PdfReader object
            
        Returns:
            int: Total word count
        """
        total_words = 0
        for page in reader.pages:
            try:
                text = page.extract_text()
                if text:
                    total_words += len(text.split())
            except Exception as e:
                logger.warning(f"Error extracting text from page: {e}")
        return total_words
    
    @staticmethod
    def get_image_count(reader):
        """
        Count the total number of images in the PDF.
        
        Args:
            reader (PdfReader): PdfReader object
            
        Returns:
            int: Total image count
        """
        total_images = 0
        for page in reader.pages:
            try:
                total_images += len(page.images)
            except Exception as e:
                logger.warning(f"Error counting images on page: {e}")
        return total_images
    
    @staticmethod
    def get_attachment_count(reader):
        """
        Count the total number of attachments in the PDF.
        
        Args:
            reader (PdfReader): PdfReader object
            
        Returns:
            int: Total attachment count
        """
        try:
            if reader.attachments:
                return len(reader.attachments)
        except Exception as e:
            logger.warning(f"Error counting attachments: {e}")
        return 0
    
    @classmethod
    def get_complete_metadata(cls, reader):
        """
        Extract all metadata from a PDF.
        
        Args:
            reader (PdfReader): PdfReader object
            
        Returns:
            dict: Complete metadata dictionary
        """
        try:
            metadata = cls.get_basic_metadata(reader)
            metadata["num_pages"] = cls.get_num_pages(reader)
            metadata["total_words"] = cls.get_total_words(reader)
            metadata["total_images"] = cls.get_image_count(reader)
            metadata["total_attachments"] = cls.get_attachment_count(reader)
            
            logger.debug(f"Extracted metadata: {metadata}")
            return metadata
        except Exception as e:
            logger.error(f"Error extracting complete metadata: {e}")
            return {}
    
    @staticmethod
    def extract_images(reader, pdf_filename, output_dir, name_template="{pdf_name}_image_{index}.{ext}"):
        """
        Extract all images from a PDF and save them to the output directory.
        
        Args:
            reader (PdfReader): PdfReader object
            pdf_filename (str): Name of the PDF file (for naming images)
            output_dir (Path or str): Directory to save extracted images
            name_template (str): Template for image filenames
            
        Returns:
            int: Number of images extracted
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_name = Path(pdf_filename).stem
        images_extracted = 0
        
        for page_num, page in enumerate(reader.pages):
            try:
                for index, img in enumerate(page.images):
                    image_data = img.data
                    
                    # Generate image filename
                    image_filename = name_template.format(
                        pdf_name=pdf_name,
                        page=page_num + 1,
                        index=images_extracted + 1,
                        ext=img.name.split('.')[-1] if '.' in img.name else 'png'
                    )
                    
                    image_path = output_dir / image_filename
                    
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_data)
                    
                    images_extracted += 1
                    logger.info(f"Extracted image: {image_path}")
                        
            except Exception as e:
                logger.error(f"Error extracting images from {pdf_filename} page {page_num + 1}: {e}")
        
        logger.info(f"Total images extracted from {pdf_filename}: {images_extracted}")
        return images_extracted

    @staticmethod
    def extract_text(reader):
        """
        Extract text from all pages of the PDF.
        
        Args:
            reader (PdfReader): PdfReader object
        Returns:
            str: Extracted text content
        """
        full_text = []
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    full_text.append(text)
            except Exception as e:
                logger.error(f"Error extracting text from page {page_num + 1}: {e}")
        
        return "\n".join(full_text)
"""
PDF-Insight: Batch PDF processing application.
Extracts metadata and images from PDF files.
"""
import logging
from pathlib import Path

import config
from pdf_processor import PDFProcessor
from file_manager import FileManager
from metadata_storage import MetadataStorage


def setup_logging():
    """Configure logging for the application."""
    config.ensure_directories()
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )


def run():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Starting PDF-Insight application")
    logger.info("=" * 60)
    
    try:
        # Initialize components
        pdf_processor = PDFProcessor()
        file_manager = FileManager()
        metadata_storage = MetadataStorage(config.METADATA_FILE)
        
        # Get all PDF files from pending directory
        pdf_files = file_manager.get_pdf_files(config.PENDING_DIR)
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {config.PENDING_DIR}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF file(s) to process")
        
        # Process each PDF file
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for pdf_path in pdf_files:
            filename = pdf_path.name
            logger.info(f"\n--- Processing: {filename} ---")
            
            try:
                # Check if already processed
                if config.SKIP_PROCESSED_FILES and metadata_storage.file_exists(filename):
                    logger.info(f"Skipping {filename} (already processed)")
                    skipped_count += 1
                    continue
                
                # Open PDF
                reader = pdf_processor.open_pdf(pdf_path)
                if not reader:
                    logger.error(f"Failed to open PDF: {filename}")
                    error_count += 1
                    continue
                
                # Extract metadata
                metadata = pdf_processor.get_complete_metadata(reader)
                if not metadata:
                    logger.error(f"Failed to extract metadata from: {filename}")
                    error_count += 1
                    continue
                
                # Save metadata
                if metadata_storage.add_metadata(filename, metadata):
                    logger.info(f"Successfully saved metadata for: {filename}")
                else:
                    logger.error(f"Failed to save metadata for: {filename}")
                
                # Extract images if configured
                if config.EXTRACT_IMAGES:
                    images_count = pdf_processor.extract_images(
                        reader, 
                        filename, 
                        config.IMAGES_DIR,
                        config.IMAGE_NAME_TEMPLATE
                    )
                    logger.info(f"Extracted {images_count} image(s) from: {filename}")
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}", exc_info=True)
                error_count += 1
                continue
        
        # Move processed files if configured
        if config.MOVE_AFTER_PROCESSING and processed_count > 0:
            logger.info(f"\nMoving processed files to {config.PROCESSED_DIR}")
            moved_count = file_manager.move_files_batch(
                config.PENDING_DIR, 
                config.PROCESSED_DIR
            )
            logger.info(f"Moved {moved_count} file(s)")
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Processing Summary:")
        logger.info(f"  Total files found: {len(pdf_files)}")
        logger.info(f"  Successfully processed: {processed_count}")
        logger.info(f"  Skipped (already processed): {skipped_count}")
        logger.info(f"  Errors: {error_count}")
        logger.info(f"  Total files in metadata: {metadata_storage.get_count()}")
        logger.info("=" * 60)
        logger.info("Application finished successfully")
        
    except Exception as e:
        logger.error(f"Critical error in application: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run()

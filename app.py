"""
PDF-Insight: Batch PDF processing application.
Extracts metadata and images from PDF files.
"""
import logging
from pathlib import Path

import config
from pdf_processor import PDFProcessor
from file_manager import FileManager
from database import Database


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
        db = Database(config.DATABASE_FILE)
        
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
                if config.SKIP_PROCESSED_FILES and db.pdf_exists(filename):
                    logger.info(f"Skipping {filename} (already processed)")
                    skipped_count += 1
                    continue
                
                # Generate unique hex ID for this PDF
                hex_id = Database.generate_hex_id(config.HEX_ID_LENGTH)
                
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
                
                # Save metadata to database and get PDF ID
                pdf_id = db.add_pdf_document(filename, metadata)
                if not pdf_id:
                    logger.error(f"Failed to save metadata for: {filename}")
                    error_count += 1
                    continue
                
                logger.info(f"Successfully saved metadata for: {filename} (PDF ID: {pdf_id})")
                
                # Extract images if configured
                if config.EXTRACT_IMAGES:
                    images_info = pdf_processor.extract_images(
                        reader, 
                        filename, 
                        config.IMAGES_DIR,
                        hex_id,
                        config.IMAGE_NAME_TEMPLATE
                    )
                    
                    # Save image references to database
                    for img_info in images_info:
                        db.add_image(
                            pdf_id,
                            img_info['filename'],
                            img_info['page'],
                            img_info['index'],
                            img_info['extension']
                        )
                    
                    logger.info(f"Extracted and registered {len(images_info)} image(s) from: {filename}")

                # Extract text if configured
                if config.EXTRACT_TEXT:
                    text_content, word_count = pdf_processor.extract_text(reader)
                    text_filename, text_file_path = file_manager.save_text_file(
                        pdf_path.stem, 
                        text_content, 
                        config.TEXT_DIR,
                        hex_id
                    )
                    
                    if text_filename and text_file_path:
                        # Save text reference to database
                        db.add_text(pdf_id, text_filename, word_count)
                        logger.info(f"Extracted text saved to: {text_file_path} ({word_count} words)")
                    else:
                        logger.error(f"Failed to save extracted text for: {filename}")
                
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
        logger.info(f"  Total PDFs in database: {db.get_pdf_count()}")
        logger.info("=" * 60)
        logger.info("Application finished successfully")
        
    except Exception as e:
        logger.error(f"Critical error in application: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run()

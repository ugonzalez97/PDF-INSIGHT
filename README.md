# PDF-Insight

**Batch PDF processing application** for extracting metadata, images, and text from PDF files with SQLite database storage.

## Features

- **Metadata Extraction**: Extracts comprehensive metadata from PDFs including title, author, pages, word count, and more
- **Image Extraction**: Automatically extracts and saves all images from PDF documents
- **Text Extraction**: Extracts full text content from PDFs
- **SQLite Database**: Stores all metadata and file references in a structured database
- **Unique File Naming**: Uses hexadecimal identifiers to prevent filename collisions
- **Batch Processing**: Processes multiple PDFs in one run
- **Deduplication**: Avoids reprocessing files that have already been analyzed
- **File Organization**: Automatically moves processed PDFs to a separate folder
- **Logging**: Comprehensive logging to both file and console
- **Modular Architecture**: Clean separation of concerns for easy maintenance and extension

## Project Structure

```
pdf-insight/
├── src/                        # Source code
│   ├── __init__.py            # Package initialization
│   ├── app.py                 # Main application logic
│   ├── config.py              # Centralized configuration
│   ├── pdf_processor.py       # PDF reading and metadata extraction
│   ├── file_manager.py        # File system operations
│   ├── database.py            # SQLite database operations
│   ├── metadata_storage.py    # Legacy JSON storage (deprecated)
│   ├── db_query.py            # Database query utility
│   └── utils.py               # Legacy utilities (deprecated)
├── tests/                      # Test suite
│   ├── __init__.py            # Test package initialization
│   ├── conftest.py            # Shared test fixtures
│   ├── test_config.py         # Config module tests
│   ├── test_database.py       # Database tests
│   ├── test_file_manager.py   # File manager tests
│   ├── test_pdf_processor.py  # PDF processor tests
│   ├── test_integration.py    # Integration tests
│   └── README.md              # Testing documentation
├── scripts/                    # Maintenance utilities
│   ├── backup_database.py     # Database backup tool
│   ├── reset_database.py      # Database reset tool
│   ├── clean_data.py          # Data cleanup tool
│   ├── move_pdfs_back.py      # PDF restoration tool
│   └── README.md              # Scripts documentation
├── main.py                     # Entry point for application
├── query.py                    # Entry point for database queries
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── pdf_insight.db              # SQLite database
├── complete_metadata.json      # Legacy metadata (for reference)
├── data/
│   ├── pending/               # Input folder for PDFs to process
│   ├── processed/             # Archive folder for processed PDFs
│   ├── images/                # Extracted images output
│   └── text/                  # Extracted text files output
└── logs/
    └── pdf_insight.log        # Application logs
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip

### Setup

1. Clone or download this repository:
   ```bash
   cd pdf-insight
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

1. Place PDF files in the `data/pending/` directory

2. Run the application:
   ```bash
   python main.py
   ```

3. Find results:
   - **Metadata**: Stored in SQLite database `pdf_insight.db`
   - **Images**: Saved in `data/images/` with unique hexadecimal identifiers
   - **Text**: Saved in `data/text/` with unique hexadecimal identifiers
   - **Processed PDFs**: Moved to `data/processed/`
   - **Logs**: Written to `logs/pdf_insight.log`

### Database Query Utility

Use the included query utility to explore the database:

```bash
# List all processed PDFs
python query.py list

# Show statistics
python query.py stats

# List all extracted files
python query.py files

# Show details for a specific PDF
python query.py show example.pdf
```

### Maintenance Scripts

Utility scripts in [scripts/](scripts/) directory:

```bash
# Backup database
python scripts/backup_database.py

# Reset database
python scripts/reset_database.py

# Clean extracted data
python scripts/clean_data.py

# Move PDFs back to pending
python scripts/move_pdfs_back.py
```

See [scripts/README.md](scripts/README.md) for detailed documentation.

### Running Tests

Run the test suite to verify functionality:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_database.py
```

See [tests/README.md](tests/README.md) for comprehensive testing documentation.

### Configuration

Edit [src/config.py](src/config.py) to customize behavior:

```python
# Processing options
EXTRACT_IMAGES = True              # Extract images from PDFs
EXTRACT_TEXT = True                # Extract text from PDFs
MOVE_AFTER_PROCESSING = True       # Move PDFs after processing
SKIP_PROCESSED_FILES = True        # Skip already processed files

# Logging
LOG_LEVEL = "INFO"                 # DEBUG, INFO, WARNING, ERROR, CRITICAL

# File naming
HEX_ID_LENGTH = 8                  # Length of hexadecimal identifiers

# Paths (customize if needed)
PENDING_DIR = DATA_DIR / "pending"
PROCESSED_DIR = DATA_DIR / "processed"
IMAGES_DIR = DATA_DIR / "images"
TEXT_DIR = DATA_DIR / "text"
DATABASE_FILE = BASE_DIR / "pdf_insight.db"
```

## Database Structure

The application uses SQLite with the following schema:

### pdf_documents table
Stores main PDF metadata:
- `id`, `filename`, `title`, `author`, `subject`, `creator`, `producer`
- `creation_date`, `modification_date`, `num_pages`, `total_words`
- `total_images`, `total_attachments`, `processed_at`

### images table
Stores references to extracted images:
- `id`, `pdf_id` (foreign key), `filename`, `page_number`, `image_index`
- `file_extension`, `extracted_at`

### texts table
Stores references to extracted text files:
- `id`, `pdf_id` (foreign key), `filename`, `word_count`, `extracted_at`

## File Naming Convention

Extracted files use hexadecimal identifiers to ensure uniqueness:
- Images: `{pdf_name}_{hex_id}_img_{index}.{ext}`
- Text: `{pdf_name}_{hex_id}_text.txt`

Example:
- `document_a3f7b9c2_img_1.png`
- `document_a3f7b9c2_text.txt`

## Key Features

This version includes:

- ✅ **SQLite Database** - Structured storage for all metadata and file references
- ✅ **Unique File Naming** - Hexadecimal identifiers prevent filename collisions
- ✅ **Text Extraction** - Full text content extraction with word counting
- ✅ **Image Extraction** - Extracts images from all pages with proper tracking
- ✅ **Modular architecture** - Separated concerns into dedicated modules
- ✅ **Deduplication** - Prevents duplicate processing
- ✅ **Configuration management** - Centralized settings in config.py
- ✅ **Proper logging** - Comprehensive logging framework
- ✅ **Better error handling** - Graceful failure handling with detailed error reporting
- ✅ **Database query utility** - Easy database exploration and analysis
- ✅ **Documentation** - Comprehensive inline documentation and README

## Dependencies

- **pypdf** (6.6.2) - PDF reading and manipulation

## Development

### Running Tests

(Tests to be implemented)

### Contributing

Contributions are welcome! Please ensure code follows the existing structure and includes appropriate logging.

## License

(Add your license here)

## Troubleshooting

### No PDFs found
- Ensure PDF files are placed in `data/pending/` directory
- Check file extensions are `.pdf` or `.PDF`

### Permission errors
- Ensure the application has write permissions for `data/` and `logs/` directories

### Memory issues with large PDFs
- Process PDFs in smaller batches
- Consider adjusting the batch size in future versions

## Future Enhancements

Potential improvements for future versions:
- CLI arguments for custom input/output directories
- Support for CSV output formats
- Progress bar for batch processing
- PDF validation before processing
- Parallel processing for large batches
- REST API for remote processing

# PDF-Insight

**Batch PDF processing application** for extracting metadata and images from PDF files.

## Features

- **Metadata Extraction**: Extracts comprehensive metadata from PDFs including title, author, pages, word count, and more
- **Image Extraction**: Automatically extracts and saves all images from PDF documents
- **Batch Processing**: Processes multiple PDFs in one run
- **Deduplication**: Avoids reprocessing files that have already been analyzed
- **File Organization**: Automatically moves processed PDFs to a separate folder
- **Logging**: Comprehensive logging to both file and console
- **Modular Architecture**: Clean separation of concerns for easy maintenance and extension

## Project Structure

```
pdf-insight/
├── app.py                      # Main application entry point
├── config.py                   # Centralized configuration
├── pdf_processor.py            # PDF reading and metadata extraction
├── file_manager.py             # File system operations
├── metadata_storage.py         # Metadata persistence with deduplication
├── utils.py                    # Legacy utilities (deprecated)
├── requirements.txt            # Python dependencies
├── complete_metadata.json      # Extracted metadata storage
├── data/
│   ├── pending/               # Input folder for PDFs to process
│   ├── processed/             # Archive folder for processed PDFs
│   └── images/                # Extracted images output
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
   python app.py
   ```

3. Find results:
   - **Metadata**: Stored in `complete_metadata.json`
   - **Images**: Saved in `data/images/`
   - **Processed PDFs**: Moved to `data/processed/`
   - **Logs**: Written to `logs/pdf_insight.log`

### Configuration

Edit [config.py](config.py) to customize behavior:

```python
# Processing options
EXTRACT_IMAGES = True              # Extract images from PDFs
MOVE_AFTER_PROCESSING = True       # Move PDFs after processing
SKIP_PROCESSED_FILES = True        # Skip already processed files

# Logging
LOG_LEVEL = "INFO"                 # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Paths (customize if needed)
PENDING_DIR = DATA_DIR / "pending"
PROCESSED_DIR = DATA_DIR / "processed"
IMAGES_DIR = DATA_DIR / "images"
```

## Metadata Structure

The application stores metadata in dictionary format for efficient lookups:

```json
{
  "example.pdf": {
    "title": "Document Title",
    "author": "Author Name",
    "subject": "Document Subject",
    "creator": "Creator Application",
    "producer": "PDF Producer",
    "creation_date": "2024-01-15T10:30:00",
    "modification_date": "2024-01-20T14:45:00",
    "num_pages": 42,
    "total_words": 8532,
    "total_images": 15,
    "total_attachments": 0,
    "processed_at": "2026-01-30T12:34:56.789123"
  }
}
```

## Key Improvements

This refactored version includes:

- ✅ **Modular architecture** - Separated concerns into dedicated modules
- ✅ **Deduplication** - Fixed critical bug preventing duplicate entries
- ✅ **Configuration management** - Centralized settings in config.py
- ✅ **Proper logging** - Replaced print statements with logging framework
- ✅ **Better error handling** - Graceful failure handling with detailed error reporting
- ✅ **Efficient data structure** - Changed from array to dictionary format for O(1) lookups
- ✅ **Automatic migration** - Converts old metadata format to new format automatically
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
- Support for CSV/SQLite output formats
- Unit tests with pytest
- Progress bar for batch processing
- PDF validation before processing
- Parallel processing for large batches

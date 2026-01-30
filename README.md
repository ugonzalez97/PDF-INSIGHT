# PDF-Insight

**Batch PDF processing application** for extracting metadata, images, and text from PDF files with SQLite database storage.

## Features

- **Metadata Extraction**: Extracts comprehensive metadata from PDFs including title, author, pages, word count, and more
- **Image Extraction**: Automatically extracts and saves all images from PDF documents
- **Text Extraction**: Extracts full text content from PDFs
- **Semantic Search**: Generate vector embeddings for intelligent content search
- **Web Interface**: Modern, responsive web UI for all operations
- **REST API**: Complete API for programmatic access
- **SQLite Database**: Stores all metadata and file references in a structured database
- **ChromaDB Vector Store**: Persistent vector database for embeddings
- **Unique File Naming**: Uses hexadecimal identifiers to prevent filename collisions
- **Batch Processing**: Processes multiple PDFs in one run
- **File Upload**: Upload PDFs directly through the web interface
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
│   ├── web_api.py             # FastAPI web application
│   ├── config.py              # Centralized configuration
│   ├── pdf_processor.py       # PDF reading and metadata extraction
│   ├── file_manager.py        # File system operations
│   ├── database.py            # SQLite database operations
│   ├── embeddings.py          # Vector embeddings management
│   ├── db_query.py            # Database query utility
│   ├── metadata_storage.py    # Legacy JSON storage (deprecated)
│   └── utils.py               # Legacy utilities (deprecated)
├── templates/                  # HTML templates for web interface
│   ├── index.html             # Home page
│   ├── pdfs.html              # PDFs list page
│   ├── pdf_detail.html        # PDF details page
│   ├── stats.html             # Statistics page
│   ├── embeddings.html        # Embeddings management page
│   ├── search.html            # Semantic search page
│   ├── upload.html            # Upload page
│   └── process.html           # Processing page
├── static/                     # Static assets
│   └── style.css              # Application styles
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
├── main.py                     # Entry point for CLI application
├── web.py                      # Entry point for web interface
├── query.py                    # Entry point for database queries
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── pdf_insight.db              # SQLite database
├── chroma_db/                  # ChromaDB vector database
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

### Web Interface

Launch the web interface for a user-friendly experience:

```bash
python web.py
```

Then open your browser at: **http://localhost:8000**

**Web Interface Features:**
- 📚 **View PDFs**: Browse all processed documents with metadata
- 📊 **Statistics**: View database statistics and analytics
- 🧠 **Embeddings**: Generate and search semantic embeddings
- 🔍 **Semantic Search**: Search through PDF content using natural language
- 📤 **Upload**: Upload PDF files through the web interface
- ⚙️ **Process PDFs**: Process new PDFs through the web UI
- 📋 **Details**: View detailed information, images, and text for each PDF
- 📥 **Download**: Download extracted text and images

**API Endpoints:**
- `GET /api/pdfs` - Get all PDFs
- `GET /api/pdf/{pdf_id}` - Get PDF details by ID
- `GET /api/pdf/by-filename/{filename}` - Get PDF by filename
- `GET /api/stats` - Get database statistics
- `GET /api/pending` - Get pending files
- `POST /api/upload` - Upload PDF files
- `POST /api/process` - Process all pending PDFs
- `GET /api/image/{filename}` - Get extracted image
- `GET /api/text/{filename}` - Get extracted text file

**Embeddings API Endpoints:**
- `POST /api/embeddings/generate/{pdf_id}` - Generate embeddings for a PDF
- `POST /api/embeddings/generate-all` - Generate embeddings for all PDFs
- `DELETE /api/embeddings/{pdf_id}` - Delete embeddings for a PDF
- `GET /api/embeddings/stats` - Get embeddings statistics
- `POST /api/search` - Search embeddings with semantic search

### Semantic Search with Embeddings

PDF-Insight includes powerful semantic search capabilities using vector embeddings:

**Features:**
- **Automatic Text Chunking**: Splits PDF text into manageable chunks
- **Vector Embeddings**: Uses sentence-transformers for high-quality embeddings
- **ChromaDB Storage**: Persistent vector database for fast similarity search
- **Semantic Search**: Find relevant content using natural language queries
- **PDF Filtering**: Search within specific PDFs or across all documents
- **Metadata Tracking**: Links embeddings to source PDFs in the database

**Usage:**
1. Process PDFs to extract text (done automatically during processing)
2. Navigate to the Embeddings page and click "Generate All Embeddings"
3. Use the Search page to find relevant content using natural language queries
4. Results show the most similar text chunks with source PDF information

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
- `total_images`, `total_attachments`, `processed_at`, `file_hash`
- `has_embeddings`, `embeddings_count`, `embeddings_generated_at`

### images table
Stores references to extracted images:
- `id`, `pdf_id` (foreign key), `filename`, `page_number`, `image_index`
- `file_extension`, `extracted_at`

### texts table
Stores references to extracted text files:
- `id`, `pdf_id` (foreign key), `filename`, `word_count`, `extracted_at`

### ChromaDB Collection
Vector embeddings are stored in ChromaDB with metadata:
- `pdf_id`, `pdf_filename`, `chunk_index`, `chunk_size`
- Each chunk includes the original text and its embedding vector

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
- ✅ **ChromaDB Vector Store** - Persistent storage for semantic embeddings
- ✅ **Web Interface** - Modern, responsive UI with FastAPI and Jinja2 templates
- ✅ **REST API** - Complete programmatic access to all functionality
- ✅ **Semantic Search** - Natural language search through PDF content
- ✅ **Text Chunking** - Intelligent text splitting for embeddings generation
- ✅ **File Upload** - Drag-and-drop PDF upload through web interface
- ✅ **Unique File Naming** - Hexadecimal identifiers prevent filename collisions
- ✅ **Text Extraction** - Full text content extraction with word counting
- ✅ **Image Extraction** - Extracts images from all pages with proper tracking
- ✅ **PDF Download** - Download original PDFs from detail pages
- ✅ **Modular architecture** - Separated concerns into dedicated modules
- ✅ **Deduplication** - Prevents duplicate processing
- ✅ **Configuration management** - Centralized settings in config.py
- ✅ **Proper logging** - Comprehensive logging framework
- ✅ **Better error handling** - Graceful failure handling with detailed error reporting
- ✅ **Database query utility** - Easy database exploration and analysis
- ✅ **Embeddings management** - Generate, delete, and regenerate embeddings per PDF
- ✅ **Statistics dashboard** - Comprehensive statistics including embeddings metrics
- ✅ **Documentation** - Comprehensive inline documentation and README

## Dependencies

### Core Dependencies
- **pypdf** (6.6.2) - PDF reading and manipulation

### Web Framework
- **fastapi** (0.109.0) - Modern web framework for building APIs
- **uvicorn** (0.27.0) - ASGI server for running FastAPI
- **jinja2** (3.1.3) - Template engine for HTML rendering
- **python-multipart** (0.0.6) - Multipart form data parsing for file uploads

### Embeddings & Vector Search
- **chromadb** (0.4.22) - Vector database for embeddings storage
- **sentence-transformers** (2.3.1) - Model for generating embeddings
- **langchain** (0.1.4) - Framework for text processing
- **langchain-community** (0.0.16) - Additional LangChain components

### Testing
- **pytest** (8.0.0) - Testing framework
- **pytest-cov** (4.1.0) - Coverage reporting
- **pytest-mock** (3.12.0) - Mocking support

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

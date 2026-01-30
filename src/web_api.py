"""
FastAPI web interface for PDF-Insight.
Provides web UI and API endpoints for all existing functionalities.
"""
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import shutil

from fastapi import FastAPI, UploadFile, File, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import config
from database import Database
from pdf_processor import PDFProcessor
from file_manager import FileManager


# Initialize FastAPI app
app = FastAPI(
    title="PDF-Insight",
    description="Batch PDF processing application for extracting metadata, images, and text",
    version="1.0.0"
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize database
db = Database(config.DATABASE_FILE)

# Setup logging
logger = logging.getLogger(__name__)


# ==================== HTML Views ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Page for uploading PDFs."""
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/pdfs", response_class=HTMLResponse)
async def pdfs_page(request: Request):
    """Page showing all processed PDFs."""
    pdfs = db.get_all_pdfs()
    return templates.TemplateResponse("pdfs.html", {
        "request": request,
        "pdfs": pdfs,
        "total": len(pdfs)
    })


@app.get("/pdf/{pdf_id}", response_class=HTMLResponse)
async def pdf_detail_page(request: Request, pdf_id: int):
    """Page showing details of a specific PDF."""
    pdf = db.get_pdf_by_id(pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    images = db.get_images_by_pdf_id(pdf_id)
    text = db.get_text_by_pdf_id(pdf_id)
    
    return templates.TemplateResponse("pdf_detail.html", {
        "request": request,
        "pdf": pdf,
        "images": images,
        "text": text
    })


@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    """Page showing database statistics."""
    pdfs = db.get_all_pdfs()
    
    if pdfs:
        total_pages = sum(pdf['num_pages'] or 0 for pdf in pdfs)
        total_words = sum(pdf['total_words'] or 0 for pdf in pdfs)
        total_images = sum(pdf['total_images'] or 0 for pdf in pdfs)
        avg_pages = total_pages / len(pdfs)
        avg_words = total_words / len(pdfs)
    else:
        total_pages = total_words = total_images = avg_pages = avg_words = 0
    
    stats = {
        "total_pdfs": len(pdfs),
        "total_pages": total_pages,
        "total_words": total_words,
        "total_images": total_images,
        "avg_pages": avg_pages,
        "avg_words": avg_words
    }
    
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "stats": stats
    })


@app.get("/process", response_class=HTMLResponse)
async def process_page(request: Request):
    """Page for processing PDFs."""
    # Get pending PDFs
    file_manager = FileManager()
    pending_files = file_manager.get_pdf_files(config.PENDING_DIR)
    pending_list = [f.name for f in pending_files]
    
    return templates.TemplateResponse("process.html", {
        "request": request,
        "pending_files": pending_list,
        "pending_count": len(pending_list)
    })


# ==================== API Endpoints ====================

@app.get("/api/pdfs")
async def get_pdfs() -> List[Dict[str, Any]]:
    """Get all processed PDFs."""
    return db.get_all_pdfs()


@app.get("/api/pdf/{pdf_id}")
async def get_pdf(pdf_id: int) -> Dict[str, Any]:
    """Get details of a specific PDF."""
    pdf = db.get_pdf_by_id(pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Add related data
    pdf['images'] = db.get_images_by_pdf_id(pdf_id)
    pdf['text'] = db.get_text_by_pdf_id(pdf_id)
    
    return pdf


@app.get("/api/pdf/by-filename/{filename}")
async def get_pdf_by_filename(filename: str) -> Dict[str, Any]:
    """Get details of a specific PDF by filename."""
    pdf = db.get_pdf_by_filename(filename)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Add related data
    pdf['images'] = db.get_images_by_pdf_id(pdf['id'])
    pdf['text'] = db.get_text_by_pdf_id(pdf['id'])
    
    return pdf


@app.get("/api/stats")
async def get_stats() -> Dict[str, Any]:
    """Get database statistics."""
    pdfs = db.get_all_pdfs()
    
    if not pdfs:
        return {
            "total_pdfs": 0,
            "total_pages": 0,
            "total_words": 0,
            "total_images": 0,
            "avg_pages": 0,
            "avg_words": 0
        }
    
    total_pages = sum(pdf['num_pages'] or 0 for pdf in pdfs)
    total_words = sum(pdf['total_words'] or 0 for pdf in pdfs)
    total_images = sum(pdf['total_images'] or 0 for pdf in pdfs)
    
    return {
        "total_pdfs": len(pdfs),
        "total_pages": total_pages,
        "total_words": total_words,
        "total_images": total_images,
        "avg_pages": total_pages / len(pdfs),
        "avg_words": total_words / len(pdfs)
    }


@app.get("/api/pending")
async def get_pending_files() -> Dict[str, Any]:
    """Get list of pending PDF files."""
    file_manager = FileManager()
    pending_files = file_manager.get_pdf_files(config.PENDING_DIR)
    
    return {
        "count": len(pending_files),
        "files": [f.name for f in pending_files]
    }


@app.post("/api/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    """Upload PDF files to pending directory."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded = []
    errors = []
    
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            errors.append(f"{file.filename}: Not a PDF file")
            continue
        
        try:
            file_path = config.PENDING_DIR / file.filename
            
            # Check if file already exists
            if file_path.exists():
                errors.append(f"{file.filename}: File already exists")
                continue
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded.append(file.filename)
            logger.info(f"Uploaded file: {file.filename}")
            
        except Exception as e:
            logger.error(f"Error uploading {file.filename}: {e}")
            errors.append(f"{file.filename}: {str(e)}")
    
    return {
        "success": True,
        "uploaded": len(uploaded),
        "files": uploaded,
        "errors": errors if errors else None
    }


@app.post("/api/process")
async def process_pdfs() -> Dict[str, Any]:
    """Process all pending PDFs."""
    try:
        pdf_processor = PDFProcessor()
        file_manager = FileManager()
        
        # Get all PDF files from pending directory
        pdf_files = file_manager.get_pdf_files(config.PENDING_DIR)
        
        if not pdf_files:
            return {
                "success": True,
                "message": "No PDF files to process",
                "processed": 0,
                "skipped": 0,
                "errors": 0
            }
        
        processed_count = 0
        skipped_count = 0
        error_count = 0
        errors = []
        
        for pdf_path in pdf_files:
            filename = pdf_path.name
            
            try:
                # Check if already processed
                if config.SKIP_PROCESSED_FILES and db.pdf_exists(filename):
                    logger.info(f"Skipping {filename} (already processed)")
                    skipped_count += 1
                    continue
                
                # Generate unique hex ID
                hex_id = Database.generate_hex_id(config.HEX_ID_LENGTH)
                
                # Open PDF
                reader = pdf_processor.open_pdf(pdf_path)
                if not reader:
                    error_count += 1
                    errors.append(f"Failed to open: {filename}")
                    continue
                
                # Extract metadata
                metadata = pdf_processor.get_complete_metadata(reader)
                if not metadata:
                    error_count += 1
                    errors.append(f"Failed to extract metadata: {filename}")
                    continue
                
                # Save metadata to database
                pdf_id = db.add_pdf_document(filename, metadata)
                if not pdf_id:
                    error_count += 1
                    errors.append(f"Failed to save metadata: {filename}")
                    continue
                
                # Extract images if configured
                if config.EXTRACT_IMAGES:
                    images_info = pdf_processor.extract_images(
                        reader, 
                        filename, 
                        config.IMAGES_DIR,
                        hex_id,
                        config.IMAGE_NAME_TEMPLATE
                    )
                    
                    for img_info in images_info:
                        db.add_image(
                            pdf_id,
                            img_info['filename'],
                            img_info['page'],
                            img_info['index'],
                            img_info['extension']
                        )
                
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
                        db.add_text(pdf_id, text_filename, word_count)
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}", exc_info=True)
                error_count += 1
                errors.append(f"{filename}: {str(e)}")
                continue
        
        # Move processed files if configured
        moved_count = 0
        if config.MOVE_AFTER_PROCESSING and processed_count > 0:
            moved_count = file_manager.move_files_batch(
                config.PENDING_DIR, 
                config.PROCESSED_DIR
            )
        
        return {
            "success": True,
            "message": f"Processing complete",
            "total": len(pdf_files),
            "processed": processed_count,
            "skipped": skipped_count,
            "errors": error_count,
            "moved": moved_count,
            "error_details": errors if errors else None
        }
        
    except Exception as e:
        logger.error(f"Critical error during processing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/image/{filename}")
async def get_image(filename: str):
    """Serve an extracted image file."""
    image_path = config.IMAGES_DIR / filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)


@app.get("/api/text/{filename}")
async def get_text(filename: str):
    """Serve an extracted text file."""
    text_path = config.TEXT_DIR / filename
    if not text_path.exists():
        raise HTTPException(status_code=404, detail="Text file not found")
    return FileResponse(text_path)

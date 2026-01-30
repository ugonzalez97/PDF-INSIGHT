#!/usr/bin/env python3
"""
Entry point for PDF-Insight web interface.
Starts the FastAPI web server.
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    import uvicorn
    from web_api import app
    
    print("=" * 60)
    print("Starting PDF-Insight Web Interface")
    print("=" * 60)
    print("Access the application at: http://localhost:8000")
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(
        "web_api:app",
        host="0.0.0.0",
        port=8011,
        reload=True,
        log_level="info"
    )

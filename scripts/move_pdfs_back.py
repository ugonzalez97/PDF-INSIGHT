#!/usr/bin/env python3
"""
Move PDFs back to pending directory.
Useful for reprocessing PDFs with updated logic.
"""
import sys
from pathlib import Path
import shutil

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import config


def move_pdfs_back():
    """Move all processed PDFs back to pending directory."""
    processed_dir = config.PROCESSED_DIR
    pending_dir = config.PENDING_DIR
    
    if not processed_dir.exists():
        print(f"✗ Processed directory does not exist: {processed_dir}")
        return
    
    # Get all PDFs
    pdf_files = list(processed_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"✓ No PDF files found in: {processed_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) in processed directory")
    print(f"\nThis will move them back to: {pending_dir}")
    
    response = input("\nContinue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("✗ Operation cancelled.")
        return
    
    # Ensure pending directory exists
    pending_dir.mkdir(parents=True, exist_ok=True)
    
    # Move files
    moved = 0
    for pdf_file in pdf_files:
        dest = pending_dir / pdf_file.name
        
        # Handle duplicates
        if dest.exists():
            print(f"  ⚠️  Skipping {pdf_file.name} (already exists in pending)")
            continue
        
        shutil.move(str(pdf_file), str(dest))
        moved += 1
        print(f"  ✓ Moved: {pdf_file.name}")
    
    print(f"\n✓ Moved {moved} file(s) back to pending directory")
    if moved < len(pdf_files):
        print(f"  Skipped {len(pdf_files) - moved} duplicate(s)")


if __name__ == "__main__":
    move_pdfs_back()

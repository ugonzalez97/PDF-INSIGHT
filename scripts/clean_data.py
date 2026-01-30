#!/usr/bin/env python3
"""
Clean data directories utility.
Removes extracted images, text files, and optionally processed PDFs.
"""
import sys
from pathlib import Path
import shutil

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import config


def count_files(directory):
    """Count files in a directory."""
    if not directory.exists():
        return 0
    return len([f for f in directory.rglob("*") if f.is_file()])


def clean_directory(directory, description):
    """Clean a directory by removing all files."""
    if not directory.exists():
        print(f"  {description}: Directory does not exist")
        return 0
    
    file_count = count_files(directory)
    if file_count == 0:
        print(f"  {description}: Already empty")
        return 0
    
    # Remove all files
    for item in directory.rglob("*"):
        if item.is_file():
            item.unlink()
    
    print(f"  {description}: Deleted {file_count} file(s)")
    return file_count


def clean_data():
    """Clean extracted data directories."""
    print("Data Cleaning Utility")
    print("=" * 50)
    
    print("\nDirectories to clean:")
    print(f"  1. Images: {config.IMAGES_DIR}")
    print(f"  2. Text: {config.TEXT_DIR}")
    print(f"  3. Processed PDFs: {config.PROCESSED_DIR}")
    
    print("\nFile counts:")
    print(f"  Images: {count_files(config.IMAGES_DIR)}")
    print(f"  Text files: {count_files(config.TEXT_DIR)}")
    print(f"  Processed PDFs: {count_files(config.PROCESSED_DIR)}")
    
    print("\n⚠️  WARNING: This will permanently delete these files!")
    
    response = input("\nWhat do you want to clean?\n"
                    "  1 - Only images and text\n"
                    "  2 - Images, text, and processed PDFs\n"
                    "  3 - Cancel\n"
                    "Choice: ")
    
    print()
    
    if response == '1':
        print("Cleaning images and text...")
        clean_directory(config.IMAGES_DIR, "Images")
        clean_directory(config.TEXT_DIR, "Text")
        print("\n✓ Cleanup complete!")
        
    elif response == '2':
        print("Cleaning images, text, and processed PDFs...")
        clean_directory(config.IMAGES_DIR, "Images")
        clean_directory(config.TEXT_DIR, "Text")
        clean_directory(config.PROCESSED_DIR, "Processed PDFs")
        print("\n✓ Cleanup complete!")
        
    else:
        print("✗ Operation cancelled.")


if __name__ == "__main__":
    clean_data()

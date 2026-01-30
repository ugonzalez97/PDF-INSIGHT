"""
Database query utility for PDF-Insight.
Provides helper functions to view and analyze the database.
"""
import sys
from pathlib import Path
from database import Database
import config


def print_separator(char="=", length=70):
    """Print a separator line."""
    print(char * length)


def show_all_pdfs(db):
    """Display all processed PDFs."""
    pdfs = db.get_all_pdfs()
    
    if not pdfs:
        print("No PDFs found in database.")
        return
    
    print_separator()
    print(f"Total PDFs: {len(pdfs)}")
    print_separator()
    
    for pdf in pdfs:
        print(f"\nID: {pdf['id']}")
        print(f"Filename: {pdf['filename']}")
        print(f"Title: {pdf['title'] or 'N/A'}")
        print(f"Author: {pdf['author'] or 'N/A'}")
        print(f"Pages: {pdf['num_pages']}")
        print(f"Words: {pdf['total_words']}")
        print(f"Images: {pdf['total_images']}")
        print(f"Processed: {pdf['processed_at']}")
        print("-" * 70)


def show_pdf_details(db, filename):
    """Display detailed information for a specific PDF."""
    pdf = db.get_pdf_by_filename(filename)
    
    if not pdf:
        print(f"PDF not found: {filename}")
        return
    
    print_separator()
    print(f"PDF Details: {filename}")
    print_separator()
    
    for key, value in pdf.items():
        print(f"{key:20}: {value}")
    
    # Show associated images
    print("\nExtracted Images:")
    print_separator("-")
    images = db.get_images_by_pdf_id(pdf['id'])
    if images:
        for img in images:
            print(f"  - {img['filename']} (Page {img['page_number']}, Index {img['image_index']})")
    else:
        print("  No images extracted")
    
    # Show associated text
    print("\nExtracted Text:")
    print_separator("-")
    text = db.get_text_by_pdf_id(pdf['id'])
    if text:
        print(f"  - {text['filename']} ({text['word_count']} words)")
    else:
        print("  No text extracted")
    
    print_separator()


def show_statistics(db):
    """Display database statistics."""
    pdfs = db.get_all_pdfs()
    
    if not pdfs:
        print("No data available.")
        return
    
    total_pages = sum(pdf['num_pages'] or 0 for pdf in pdfs)
    total_words = sum(pdf['total_words'] or 0 for pdf in pdfs)
    total_images_count = sum(pdf['total_images'] or 0 for pdf in pdfs)
    
    print_separator()
    print("Database Statistics")
    print_separator()
    print(f"Total PDFs processed: {len(pdfs)}")
    print(f"Total pages: {total_pages}")
    print(f"Total words: {total_words:,}")
    print(f"Total images: {total_images_count}")
    print(f"Average pages per PDF: {total_pages / len(pdfs):.1f}")
    print(f"Average words per PDF: {total_words / len(pdfs):,.0f}")
    print_separator()


def list_files(db):
    """List all extracted files (images and texts)."""
    pdfs = db.get_all_pdfs()
    
    print_separator()
    print("Extracted Files")
    print_separator()
    
    total_images = 0
    total_texts = 0
    
    for pdf in pdfs:
        images = db.get_images_by_pdf_id(pdf['id'])
        text = db.get_text_by_pdf_id(pdf['id'])
        
        if images or text:
            print(f"\n{pdf['filename']}:")
            
            if images:
                print(f"  Images ({len(images)}):")
                for img in images:
                    print(f"    - {img['filename']}")
                total_images += len(images)
            
            if text:
                print(f"  Text:")
                print(f"    - {text['filename']}")
                total_texts += 1
    
    print_separator()
    print(f"Total: {total_images} images, {total_texts} text files")
    print_separator()


def main():
    """Main entry point for database query utility."""
    db = Database(config.DATABASE_FILE)
    
    if len(sys.argv) < 2:
        print("PDF-Insight Database Query Utility")
        print_separator()
        print("Usage:")
        print("  python db_query.py list            - List all PDFs")
        print("  python db_query.py stats           - Show statistics")
        print("  python db_query.py files           - List all extracted files")
        print("  python db_query.py show <filename> - Show PDF details")
        print_separator()
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        show_all_pdfs(db)
    elif command == "stats":
        show_statistics(db)
    elif command == "files":
        list_files(db)
    elif command == "show" and len(sys.argv) > 2:
        filename = sys.argv[2]
        show_pdf_details(db, filename)
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()

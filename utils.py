from pypdf import PdfReader


def get_basic_metadata(reader):
    """Extract metadata from a PdfReader object."""
    metadata = reader.metadata

    # Parse date fields if they exist
    def parse_date(date_str):
        from datetime import datetime
        if isinstance(date_str, datetime):
            return date_str.isoformat()

    return {
        "title": metadata.title,
        "author": metadata.author,
        "subject": metadata.subject,
        "creator": metadata.creator,
        "producer": metadata.producer,
        "creation_date": parse_date(metadata.creation_date),
        "modification_date": parse_date(metadata.modification_date),
    }


def get_num_pages(reader):
    """Return the number of pages in the PDF."""
    return {"num_pages": len(reader.pages)}


def get_total_words(reader):
    """Count the total number of words in the PDF."""
    total_words = 0
    for page in reader.pages:
        text = page.extract_text()
        if text:
            total_words += len(text.split())
    return {"total_words": total_words}


def get_image_count(reader):
    """Count the total number of images in the PDF."""
    total_images = 0
    for page in reader.pages:
        total_images += len(page.images)
    return {"total_images": total_images}


def get_attachment_count(reader):
    """Count the total number of attachments in the PDF."""
    if reader.attachments:
        return {"total_attachments": len(reader.attachments)}
    return {"total_attachments": 0}


def write_metadata_to_json(metadata, file_path):
    """Write metadata dictionary to a JSON file. Inlcude count of entries."""
    import json
    try:
        with open(file_path, 'w') as f:
            entries_count = len(metadata)
            metadata_with_count = {"entries_count": entries_count, **metadata}
            json.dump(metadata_with_count, f, indent=4)
        print(f"Metadata written to {file_path}")
    except Exception as e:
        print(f"Error writing metadata to file: {e}")


def get_pdf_reader(file_path):
    """Open a PDF file and return a PdfReader object."""
    try:
        reader = PdfReader(file_path)
        return reader
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        return None


def get_metadata(reader):
    metadata = get_basic_metadata(reader)
    num_pages = get_num_pages(reader)
    total_words = get_total_words(reader)
    image_count = get_image_count(reader)
    attachment_count = get_attachment_count(reader)

    return {**metadata, **num_pages, **total_words, **image_count, **attachment_count}


def get_all_readers(folder_path):
    """Get PdfReader objects for all PDF files in a folder."""
    import os
    readers = []

    if not os.path.isdir(folder_path):
        print(f"The folder path {folder_path} does not exist or is not a directory.")
        return readers

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            reader = get_pdf_reader(file_path)
            if reader:
                readers.append((filename, reader))
    return readers

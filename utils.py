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


def append_metadata_to_json(filename, metadata, file_path="complete_metadata.json"):
    """Write metadata dictionary to a JSON file. Maintain a list of entries."""
    import json
    import os

    try:
        # Read existing data if file exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    # Ensure data is a list
                    if not isinstance(data, list):
                        data = [data]
                except json.JSONDecodeError:
                    # File is empty or invalid, start fresh
                    data = []
        else:
            data = []

        # Append new metadata
        data.append({filename: metadata})

        # Write back to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Metadata written to {file_path}. Total entries: {len(data)}")
    except Exception as e:
        print(f"Error writing metadata to file: {e}")


def extract_images_from_pdf(reader, filename, output_folder="data/images"):
    """Extract images from a PDF and save them to the specified output folder."""
    import os

    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for page_num, page in enumerate(reader.pages):
            for img_index, img in enumerate(page.images):
                image_data = img.data
                image_filename = f"{os.path.splitext(filename)[0]}_page{page_num+1}_img{img_index+1}.{img.name}"
                image_path = os.path.join(output_folder, image_filename)

                with open(image_path, 'wb') as img_file:
                    img_file.write(image_data)

                print(f"Extracted image to {image_path}")
    except Exception as e:
        print(f"Error extracting images from {filename}: {e}")


def move_files_to_processed_folder(source_folder="data/pending", dest_folder="data/processed"):
    """Move processed files to a 'processed' folder."""
    import os
    import shutil

    try:
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        for file_name in os.listdir(source_folder):
            source_path = os.path.join(source_folder, file_name)
            dest_path = os.path.join(dest_folder, file_name)

            shutil.move(source_path, dest_path)
            print(f"Moved {file_name} to {dest_folder}")
    except Exception as e:
        print(f"Error moving file {file_name}: {e}")


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
        print(
            f"The folder path {folder_path} does not exist or is not a directory.")
        return readers

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            reader = get_pdf_reader(file_path)
            if reader:
                readers.append((filename, reader))
    return readers

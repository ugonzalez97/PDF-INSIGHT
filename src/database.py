"""
Database module for managing PDF metadata and extracted content using SQLite.
"""
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
import secrets

logger = logging.getLogger(__name__)


class Database:
    """Handle SQLite database operations for PDF metadata and content."""
    
    def __init__(self, db_path):
        """
        Initialize database connection and create tables if needed.
        
        Args:
            db_path (str or Path): Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
        logger.info(f"Database initialized: {self.db_path}")
    
    def _get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(str(self.db_path))
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # PDF documents table (main metadata)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pdf_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    title TEXT,
                    author TEXT,
                    subject TEXT,
                    creator TEXT,
                    producer TEXT,
                    creation_date TEXT,
                    modification_date TEXT,
                    num_pages INTEGER,
                    total_words INTEGER,
                    total_images INTEGER,
                    total_attachments INTEGER,
                    processed_at TEXT NOT NULL,
                    file_hash TEXT
                )
            ''')
            
            # Images table (references to extracted images)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pdf_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    image_index INTEGER NOT NULL,
                    file_extension TEXT,
                    extracted_at TEXT NOT NULL,
                    FOREIGN KEY (pdf_id) REFERENCES pdf_documents (id) ON DELETE CASCADE
                )
            ''')
            
            # Texts table (references to extracted text files)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS texts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pdf_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    word_count INTEGER,
                    extracted_at TEXT NOT NULL,
                    FOREIGN KEY (pdf_id) REFERENCES pdf_documents (id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pdf_filename ON pdf_documents(filename)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_pdf_id ON images(pdf_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_texts_pdf_id ON texts(pdf_id)')
            
            conn.commit()
            logger.debug("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    @staticmethod
    def generate_hex_id(length=8):
        """
        Generate a random hexadecimal identifier.
        
        Args:
            length (int): Length of the hex string
            
        Returns:
            str: Random hexadecimal string
        """
        return secrets.token_hex(length // 2)
    
    def pdf_exists(self, filename):
        """
        Check if a PDF has already been processed.
        
        Args:
            filename (str): Name of the PDF file
            
        Returns:
            bool: True if file exists in database, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM pdf_documents WHERE filename = ?', (filename,))
            result = cursor.fetchone()
            return result is not None
        finally:
            conn.close()
    
    def add_pdf_document(self, filename, metadata):
        """
        Add or update PDF document metadata.
        
        Args:
            filename (str): Name of the PDF file
            metadata (dict): Metadata dictionary
            
        Returns:
            int or None: PDF document ID if successful, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            processed_at = datetime.now().isoformat()
            
            # Check if document already exists
            cursor.execute('SELECT id FROM pdf_documents WHERE filename = ?', (filename,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                pdf_id = existing[0]
                cursor.execute('''
                    UPDATE pdf_documents SET
                        title = ?, author = ?, subject = ?, creator = ?,
                        producer = ?, creation_date = ?, modification_date = ?,
                        num_pages = ?, total_words = ?, total_images = ?,
                        total_attachments = ?, processed_at = ?
                    WHERE id = ?
                ''', (
                    metadata.get('title'),
                    metadata.get('author'),
                    metadata.get('subject'),
                    metadata.get('creator'),
                    metadata.get('producer'),
                    metadata.get('creation_date'),
                    metadata.get('modification_date'),
                    metadata.get('num_pages'),
                    metadata.get('total_words'),
                    metadata.get('total_images'),
                    metadata.get('total_attachments'),
                    processed_at,
                    pdf_id
                ))
                logger.info(f"Updated existing PDF document: {filename}")
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO pdf_documents (
                        filename, title, author, subject, creator, producer,
                        creation_date, modification_date, num_pages, total_words,
                        total_images, total_attachments, processed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    filename,
                    metadata.get('title'),
                    metadata.get('author'),
                    metadata.get('subject'),
                    metadata.get('creator'),
                    metadata.get('producer'),
                    metadata.get('creation_date'),
                    metadata.get('modification_date'),
                    metadata.get('num_pages'),
                    metadata.get('total_words'),
                    metadata.get('total_images'),
                    metadata.get('total_attachments'),
                    processed_at
                ))
                pdf_id = cursor.lastrowid
                logger.info(f"Added new PDF document: {filename} (ID: {pdf_id})")
            
            conn.commit()
            return pdf_id
            
        except Exception as e:
            logger.error(f"Error adding PDF document {filename}: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def add_image(self, pdf_id, filename, page_number, image_index, file_extension):
        """
        Add image reference to database.
        
        Args:
            pdf_id (int): PDF document ID
            filename (str): Image filename
            page_number (int): Page number where image was extracted
            image_index (int): Index of image on the page
            file_extension (str): File extension (jpg, png, etc.)
            
        Returns:
            int or None: Image ID if successful, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            extracted_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO images (pdf_id, filename, page_number, image_index, 
                                    file_extension, extracted_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (pdf_id, filename, page_number, image_index, file_extension, extracted_at))
            
            image_id = cursor.lastrowid
            conn.commit()
            logger.debug(f"Added image reference: {filename} (ID: {image_id})")
            return image_id
            
        except Exception as e:
            logger.error(f"Error adding image reference {filename}: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def add_text(self, pdf_id, filename, word_count=None):
        """
        Add text file reference to database.
        
        Args:
            pdf_id (int): PDF document ID
            filename (str): Text filename
            word_count (int, optional): Word count in the text
            
        Returns:
            int or None: Text ID if successful, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            extracted_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO texts (pdf_id, filename, word_count, extracted_at)
                VALUES (?, ?, ?, ?)
            ''', (pdf_id, filename, word_count, extracted_at))
            
            text_id = cursor.lastrowid
            conn.commit()
            logger.debug(f"Added text reference: {filename} (ID: {text_id})")
            return text_id
            
        except Exception as e:
            logger.error(f"Error adding text reference {filename}: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def get_pdf_by_filename(self, filename):
        """
        Get PDF document by filename.
        
        Args:
            filename (str): Name of the PDF file
            
        Returns:
            dict or None: PDF document data if found, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM pdf_documents WHERE filename = ?', (filename,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
            
        finally:
            conn.close()
    
    def get_images_by_pdf_id(self, pdf_id):
        """
        Get all images for a PDF document.
        
        Args:
            pdf_id (int): PDF document ID
            
        Returns:
            list: List of image dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM images WHERE pdf_id = ?', (pdf_id,))
            rows = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
            
        finally:
            conn.close()
    
    def get_text_by_pdf_id(self, pdf_id):
        """
        Get text file for a PDF document.
        
        Args:
            pdf_id (int): PDF document ID
            
        Returns:
            dict or None: Text file data if found, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM texts WHERE pdf_id = ?', (pdf_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
            
        finally:
            conn.close()
    
    def get_all_pdfs(self):
        """
        Get all PDF documents.
        
        Returns:
            list: List of PDF document dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM pdf_documents ORDER BY processed_at DESC')
            rows = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
            
        finally:
            conn.close()
    
    def get_pdf_count(self):
        """
        Get total number of processed PDFs.
        
        Returns:
            int: Number of processed PDFs
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM pdf_documents')
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def delete_pdf(self, filename):
        """
        Delete a PDF document and all its related data.
        
        Args:
            filename (str): Name of the PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM pdf_documents WHERE filename = ?', (filename,))
            deleted = cursor.rowcount > 0
            conn.commit()
            
            if deleted:
                logger.info(f"Deleted PDF document and related data: {filename}")
            else:
                logger.warning(f"No PDF document found to delete: {filename}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting PDF document {filename}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

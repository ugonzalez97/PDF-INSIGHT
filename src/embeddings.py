"""
Embeddings module for PDF-Insight.
Handles text chunking, embedding generation, and vector storage using ChromaDB.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """Manage embeddings generation and storage using ChromaDB."""
    
    def __init__(self, persist_directory: str = "./chroma_db", 
                 model_name: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 500,
                 chunk_overlap: int = 50):
        """
        Initialize the embeddings manager.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            model_name: Name of the sentence-transformers model to use
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="pdf_embeddings",
            metadata={"description": "PDF document embeddings"}
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info(f"Embeddings manager initialized with model: {model_name}")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        chunks = self.text_splitter.split_text(text)
        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def add_pdf_embeddings(self, pdf_id: int, pdf_filename: str, text: str) -> int:
        """
        Process a PDF's text and add embeddings to the collection.
        
        Args:
            pdf_id: Database ID of the PDF
            pdf_filename: Name of the PDF file
            text: Full text content of the PDF
            
        Returns:
            Number of chunks/embeddings created
        """
        # Split text into chunks
        chunks = self.chunk_text(text)
        
        if not chunks:
            logger.warning(f"No chunks generated for PDF ID {pdf_id}")
            return 0
        
        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)
        
        # Prepare IDs and metadata
        ids = [f"pdf_{pdf_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "pdf_id": pdf_id,
                "pdf_filename": pdf_filename,
                "chunk_index": i,
                "chunk_size": len(chunk)
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(chunks)} embeddings for PDF ID {pdf_id}: {pdf_filename}")
        return len(chunks)
    
    def delete_pdf_embeddings(self, pdf_id: int) -> int:
        """
        Delete all embeddings for a specific PDF.
        
        Args:
            pdf_id: Database ID of the PDF
            
        Returns:
            Number of embeddings deleted
        """
        # Query all IDs for this PDF
        results = self.collection.get(
            where={"pdf_id": pdf_id}
        )
        
        if not results['ids']:
            logger.info(f"No embeddings found for PDF ID {pdf_id}")
            return 0
        
        # Delete embeddings
        self.collection.delete(ids=results['ids'])
        
        count = len(results['ids'])
        logger.info(f"Deleted {count} embeddings for PDF ID {pdf_id}")
        return count
    
    def search_embeddings(self, query: str, n_results: int = 10, 
                         pdf_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Search for similar text chunks using semantic search.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            pdf_id: Optional PDF ID to filter results
            
        Returns:
            Dictionary with search results
        """
        # Generate query embedding
        query_embedding = self.model.encode([query])[0].tolist()
        
        # Prepare where filter
        where_filter = {"pdf_id": pdf_id} if pdf_id else None
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return {
            "query": query,
            "n_results": len(formatted_results),
            "results": formatted_results
        }
    
    def get_pdf_embedding_count(self, pdf_id: int) -> int:
        """
        Get the number of embeddings for a specific PDF.
        
        Args:
            pdf_id: Database ID of the PDF
            
        Returns:
            Number of embeddings
        """
        results = self.collection.get(
            where={"pdf_id": pdf_id}
        )
        return len(results['ids']) if results['ids'] else 0
    
    def get_all_pdf_ids_with_embeddings(self) -> List[int]:
        """
        Get list of all PDF IDs that have embeddings.
        
        Returns:
            List of PDF IDs
        """
        # Get all items
        results = self.collection.get()
        
        if not results['metadatas']:
            return []
        
        # Extract unique PDF IDs
        pdf_ids = set()
        for metadata in results['metadatas']:
            if 'pdf_id' in metadata:
                pdf_ids.add(metadata['pdf_id'])
        
        return sorted(list(pdf_ids))
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the embeddings collection.
        
        Returns:
            Dictionary with collection statistics
        """
        results = self.collection.get()
        
        total_embeddings = len(results['ids']) if results['ids'] else 0
        pdf_ids = self.get_all_pdf_ids_with_embeddings()
        
        return {
            "total_embeddings": total_embeddings,
            "total_pdfs_with_embeddings": len(pdf_ids),
            "model_name": self.model_name,
            "collection_name": self.collection.name
        }

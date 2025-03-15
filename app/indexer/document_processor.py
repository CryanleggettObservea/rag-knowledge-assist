import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from your specific location
load_dotenv("/Users/chrisrleggett/Desktop/2025 Year of Snake/Interview Prep/local files/.env")

class DocumentProcessor:
    def __init__(self):
        self.documents_dir = os.getenv("DOCUMENTS_DIR", "./app/data/documents")
        self.chroma_db_dir = os.getenv("CHROMA_DB_DIR", "./app/data/chromadb")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))
        
        # Initialize embeddings model
        logger.info("Initializing HuggingFace embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        
    def load_documents(self) -> List:
        """Load documents from the documents directory."""
        logger.info(f"Loading documents from {self.documents_dir}")
        documents = []
        
        # Check if directory exists
        if not os.path.exists(self.documents_dir):
            logger.warning(f"Documents directory {self.documents_dir} does not exist. Creating it.")
            os.makedirs(self.documents_dir, exist_ok=True)
            return documents
            
        for file in os.listdir(self.documents_dir):
            file_path = os.path.join(self.documents_dir, file)
            try:
                if file.endswith('.pdf'):
                    logger.info(f"Loading PDF: {file}")
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                elif file.endswith('.txt'):
                    logger.info(f"Loading text file: {file}")
                    loader = TextLoader(file_path)
                    documents.extend(loader.load())
            except Exception as e:
                logger.error(f"Error loading file {file}: {str(e)}")
        
        logger.info(f"Loaded {len(documents)} document(s)")
        return documents
    
    def split_documents(self, documents):
        """Split documents into chunks."""
        if not documents:
            logger.warning("No documents to split")
            return []
            
        logger.info(f"Splitting documents into chunks (size: {self.chunk_size}, overlap: {self.chunk_overlap})")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def create_vector_store(self, chunks):
        """Create or update the vector store with document chunks."""
        if not chunks:
            logger.warning("No chunks to index")
            return None
            
        logger.info(f"Creating/updating vector store at {self.chroma_db_dir}")
        
        # Ensure directory exists
        os.makedirs(self.chroma_db_dir, exist_ok=True)
        
        return Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.chroma_db_dir
        )
    
    def process_documents(self):
        """Process documents and create vector store."""
        logger.info("Starting document processing pipeline")
        documents = self.load_documents()
        if not documents:
            logger.warning("No documents found to process")
            return 0
            
        chunks = self.split_documents(documents)
        if not chunks:
            logger.warning("No chunks created")
            return 0
            
        vector_store = self.create_vector_store(chunks)
        if vector_store:
            vector_store.persist()
            logger.info("Vector store created and persisted successfully")
        
        return len(chunks)

if __name__ == "__main__":
    processor = DocumentProcessor()
    num_chunks = processor.process_documents()
    print(f"Processed {num_chunks} document chunks.")
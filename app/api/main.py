from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ..utils.document_watcher import DocumentWatcher
from typing import List, Optional
import os
import shutil
from pathlib import Path
import logging

from app.retriever.rag_retriever import RAGRetriever
from app.indexer.document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="RAG Knowledge Assistant")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG components
documents_dir = os.getenv("DOCUMENTS_DIR", "./app/data/documents")
Path(documents_dir).mkdir(parents=True, exist_ok=True)

# Initialize on startup instead of at module level
retriever = None
processor = None

@app.on_event("startup")
async def startup_event():
    global retriever, processor
    logger.info("Initializing RAG components...")
    
    # Initialize the document processor
    processor = DocumentProcessor()
    
    # Process any documents in the documents directory
    logger.info("Checking for documents to process...")
    num_chunks = processor.process_documents()
    logger.info(f"Processed {num_chunks} document chunks on startup")
    
    # Initialize the retriever AFTER processing documents
    retriever = RAGRetriever()
    
    # Start document watcher (check for updates every 30 seconds)
    watcher = DocumentWatcher(documents_dir, check_interval=30)
    watcher.start()
    
    logger.info("RAG components initialized")

class Query(BaseModel):
    text: str
    max_results: Optional[int] = 4

class Response(BaseModel):
    answer: str
    sources: List[str]

@app.get("/")
def read_root():
    return {"message": "RAG Knowledge Assistant API"}

@app.post("/query", response_model=Response)
async def query(query: Query):
    if not retriever:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    try:
        logger.info(f"Received query: {query.text}")
        answer, sources = retriever.query(query.text)
        return Response(
            answer=answer,
            sources=sources
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not processor:
        raise HTTPException(status_code=500, detail="Document processor not initialized")
        
    try:
        logger.info(f"Received file: {file.filename}")
        # Save the file
        file_path = os.path.join(documents_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process documents
        num_chunks = processor.process_documents()
        logger.info(f"Processed {num_chunks} document chunks after upload")
        
        # Reinitialize the retriever to use the updated vector store
        global retriever
        retriever = RAGRetriever()
        
        return {"message": f"File uploaded successfully and processed into {num_chunks} chunks"}
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    try:
        files = os.listdir(documents_dir)
        return {"documents": files}
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
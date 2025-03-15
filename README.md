# RAG Knowledge Assistant

A domain-specific knowledge assistant using Retrieval Augmented Generation (RAG) to provide accurate, contextual responses to user queries.

## Features

- Document ingestion (PDF and text files)
- Vector database storage with Chroma
- RAG-based query answering using Claude AI
- FastAPI backend
- Automatic document monitoring and processing
- Simple API for integration

## Setup

### Prerequisites

Install all required dependencies with a single command:

```bash
pip3 install "langchain>=0.0.267" "langchain-community>=0.0.1" "langchain-anthropic>=0.1.1" "anthropic>=0.5.0" "sentence-transformers>=2.2.2" "chromadb>=0.4.6" "fastapi>=0.100.0" "uvicorn>=0.23.0" "pypdf>=3.15.0" "python-multipart"
```

### Environment Setup

This project uses environment variables for configuration:

1. Copy the example environment file to create your local environment:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file with your own values:
   - Add your Anthropic API key (get one at https://console.anthropic.com/)
   - Adjust other settings as needed

Note: The `.env` file is ignored by Git to avoid exposing your API key. Never commit sensitive credentials to the repository.

## Project Structure

```
rag-knowledge-assist/
├── app/
│   ├── api/
│   │   └── main.py          # FastAPI application and endpoints
│   ├── indexer/
│   │   └── document_processor.py  # Document loading and processing
│   ├── retriever/
│   │   └── rag_retriever.py       # RAG implementation with Claude
│   ├── utils/
│   │   └── document_watcher.py    # Automatic document monitoring
│   ├── data/
│   │   ├── documents/       # Directory for source documents
│   │   └── chromadb/        # Vector database storage
│   └── main.py              # Application entry point
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore file
└── README.md                # This file
```

## Running the Application

1. Ensure all dependencies are installed (see Prerequisites)
2. Set up your environment variables (see Environment Setup)
3. Run the application:
   ```
   python3 -m app.main
   ```
4. The API will be available at http://localhost:8000
5. API documentation is available at http://localhost:8000/docs

## Using the Application

### Adding Documents

There are two ways to add documents to the system:

1. **Through the API**:
   - Go to http://localhost:8000/docs
   - Navigate to the `/upload` endpoint
   - Click "Try it out"
   - Use the file selector to choose a document (PDF or text)
   - Click "Execute"

2. **Directly to the documents folder**:
   - Add PDF or text files to the `app/data/documents` directory
   - The system will automatically detect and process these files

### Querying the System

1. Go to http://localhost:8000/docs
2. Navigate to the `/query` endpoint
3. Click "Try it out"
4. Enter your query in the text field:
   ```json
   {
     "text": "What are the key benefits of RAG systems?",
     "max_results": 4
   }
   ```
5. Click "Execute"
6. The system will return an answer based on your documents, with source references

### Listing Documents

To see all documents in the system:

1. Go to http://localhost:8000/docs
2. Navigate to the `/documents` endpoint
3. Click "Try it out" then "Execute"

## How It Works

The RAG Knowledge Assistant works as follows:

1. **Document Processing**:
   - Documents are loaded from the `app/data/documents` directory
   - Text is extracted and split into manageable chunks
   - Each chunk is converted to a vector embedding
   - Embeddings are stored in a Chroma vector database

2. **Querying**:
   - User query is converted to an embedding
   - System finds the most semantically relevant chunks
   - Retrieved chunks are sent to Claude AI as context
   - Claude generates a response based on this context

3. **Automatic Updates**:
   - The system periodically checks for document changes
   - New or modified documents are automatically processed
   - Deleted documents are removed from the knowledge base

## Future Enhancements

- Web-based user interface
- Support for more document types (HTML, Markdown, etc.)
- Advanced chunking strategies
- User authentication and multi-user support
- Enhanced prompt engineering
- Cloud deployment configurations

## Troubleshooting

- If Claude API integration is not working, check your API key and model name
- If documents aren't being processed, check file permissions in the documents directory
- For other issues, check the application logs for detailed error messages

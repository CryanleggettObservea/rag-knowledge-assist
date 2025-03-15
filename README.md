# rag-knowledge-assist
A domain-specific knowledge assistant using Retrieval Augmented Generation (RAG) to provide accurate, contextual responses to user queries.

## Environment Setup

This project uses environment variables for configuration:

1. Copy the example environment file to create your local environment:


2. Edit the `.env` file with your own values:
- Add your Anthropic API key (get one at https://console.anthropic.com/)
- Adjust other settings as needed

Note: The `.env` file is ignored by Git to avoid exposing your API key. Never commit sensitive credentials to the repository.

## Install dependencies

## Install required packages

anthropic
python-dotenv
langchain
langchain-anthropic
sentence-transformers
chromadb
fastapi
uvicorn
pypdf

You can simply run this one lin before running this project and replacing your actual API keys to install packages:  
pip3 install "langchain>=0.0.267" "langchain-community>=0.0.1" "langchain-anthropic>=0.1.1" "anthropic>=0.5.0" "sentence-transformers>=2.2.2" "chromadb>=0.4.6" "fastapi>=0.100.0" "uvicorn>=0.23.0" "pypdf>=3.15.0"
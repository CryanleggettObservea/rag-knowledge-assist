import os
from typing import List, Tuple
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from your specific location
load_dotenv("/Users/chrisrleggett/Desktop/2025 Year of Snake/Interview Prep/local files/.env")

class RAGRetriever:
    def __init__(self):
        self.chroma_db_dir = os.getenv("CHROMA_DB_DIR", "./app/data/chromadb")
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620")
        
        logger.info("Initializing RAG Retriever")
        
        # Initialize embeddings
        logger.info("Initializing embeddings model")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        
        # Initialize Claude LLM
        logger.info(f"Initializing Claude model: {self.claude_model}")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("No Anthropic API key found in environment variables")
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
        self.llm = ChatAnthropic(
            model=self.claude_model,
            temperature=0.1,
            anthropic_api_key=api_key
        )
        
        # Initialize vector store if it exists
        if os.path.exists(self.chroma_db_dir):
            logger.info(f"Loading vector store from {self.chroma_db_dir}")
            self.vector_store = Chroma(
                persist_directory=self.chroma_db_dir,
                embedding_function=self.embeddings
            )
            
            # Create QA chain
            self.qa_prompt = PromptTemplate(
                template="""You are a helpful assistant that provides accurate information based on the given context.
                
                Context:
                {context}
                
                Question: {question}
                
                Answer the question based on the provided context. If the answer is not in the context, say that you don't have enough information. Keep your answer concise and to the point.""",
                input_variables=["context", "question"]
            )
            
            self.qa_chain = self._create_qa_chain()
        else:
            logger.warning(f"Vector store directory {self.chroma_db_dir} does not exist")
            self.vector_store = None
            self.qa_chain = None
        
    def _create_qa_chain(self):
        """Create a retrieval QA chain."""
        logger.info("Creating QA chain")
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": self.qa_prompt},
            return_source_documents=True
        )
    
    def query(self, question: str) -> Tuple[str, List[str]]:
        """
        Query the RAG system with a question.
        
        Args:
            question: The question to ask
            
        Returns:
            Tuple of (answer, source_documents)
        """
        if not self.qa_chain:
            logger.error("QA chain is not initialized. Make sure the vector store exists.")
            return "I'm not able to answer questions yet. Please add some documents first.", []
        
        logger.info(f"Querying: {question}")
        try:
            result = self.qa_chain({"query": question})
            sources = [doc.metadata.get("source", "Unknown") for doc in result["source_documents"]]
            logger.info(f"Query successful, found {len(sources)} sources")
            return result["result"], sources
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            return f"An error occurred: {str(e)}", []

if __name__ == "__main__":
    # Simple test
    retriever = RAGRetriever()
    answer, sources = retriever.query("What is RAG?")
    print(f"Answer: {answer}")
    print(f"Sources: {sources}")
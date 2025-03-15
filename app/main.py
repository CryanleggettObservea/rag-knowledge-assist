import uvicorn
import logging
import os
from dotenv import load_dotenv

# Load environment variables from your specific location
load_dotenv("/Users/chrisrleggett/Desktop/2025 Year of Snake/Interview Prep/local files/.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting RAG Knowledge Assistant API")
    
    # Get port from environment or use default
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    # Run API
    uvicorn.run(
        "app.api.main:app", 
        host=host, 
        port=port, 
        reload=True,
        log_level="info"
    )
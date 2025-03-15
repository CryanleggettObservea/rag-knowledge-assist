import os
import time
import threading
import logging
from pathlib import Path
from app.indexer.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class DocumentWatcher:
    def __init__(self, documents_dir, check_interval=60):
        """
        Initialize a document watcher that periodically checks for changes.
        
        Args:
            documents_dir: Directory containing documents
            check_interval: How often to check for updates (in seconds)
        """
        self.documents_dir = documents_dir
        self.check_interval = check_interval
        self.processor = DocumentProcessor()
        self.file_mtimes = {}  # Track file modification times
        self.running = False
        self.thread = None
        
    def _get_current_mtimes(self):
        """Get current modification times of all documents."""
        mtimes = {}
        if os.path.exists(self.documents_dir):
            for filename in os.listdir(self.documents_dir):
                file_path = os.path.join(self.documents_dir, filename)
                if os.path.isfile(file_path):
                    mtimes[filename] = os.path.getmtime(file_path)
        return mtimes
        
    def _check_for_updates(self):
        """Check for document updates."""
        current_mtimes = self._get_current_mtimes()
        
        # Check for new or modified files
        updated = False
        for filename, mtime in current_mtimes.items():
            if filename not in self.file_mtimes or self.file_mtimes[filename] < mtime:
                logger.info(f"Detected new or updated file: {filename}")
                updated = True
                break
                
        # Check for deleted files
        for filename in list(self.file_mtimes.keys()):
            if filename not in current_mtimes:
                logger.info(f"Detected removed file: {filename}")
                updated = True
                break
                
        # Update tracked mtimes
        self.file_mtimes = current_mtimes
        
        # Process documents if changes detected
        if updated:
            logger.info("Changes detected, reprocessing documents...")
            num_chunks = self.processor.process_documents()
            logger.info(f"Processed {num_chunks} document chunks")
            return True
            
        return False
    
    def _watch_loop(self):
        """Main watching loop."""
        logger.info(f"Document watcher started, checking every {self.check_interval} seconds")
        while self.running:
            try:
                self._check_for_updates()
            except Exception as e:
                logger.error(f"Error checking for document updates: {str(e)}")
            
            # Sleep for check_interval
            time.sleep(self.check_interval)
    
    def start(self):
        """Start the document watcher."""
        if self.thread and self.thread.is_alive():
            logger.warning("Document watcher already running")
            return
            
        # Initialize current file state
        self.file_mtimes = self._get_current_mtimes()
        
        # Start watching thread
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop the document watcher."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
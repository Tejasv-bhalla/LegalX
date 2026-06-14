import sys
import os
from pathlib import Path

# Add backend directory to path
backend_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(backend_path)

from core.logging_config import logger
from pipeline.loader import load_and_clean_pdf
from pipeline.splitter import split_documents
from storage.database import init_db, save_topic_metadata, get_topic_metadata

def run_verification():
    logger.info("=== Starting Pipeline Phase 2 Verification ===")
    
    # 1. Initialize SQLite Database
    init_db()
    
    # 2. Load and clean sample PDF (POCSO Act)
    pdf_path = os.path.join(backend_path, "data", "sources", "pocso.pdf")
    if not os.path.exists(pdf_path):
        logger.error(f"Sample PDF not found at {pdf_path}. Cannot complete parser verification.")
        sys.exit(1)
        
    try:
        pages = load_and_clean_pdf(pdf_path)
        logger.info(f"Verification: Successfully parsed {len(pages)} content pages.")
        
        # Verify Table of Contents was skipped
        for i, page in enumerate(pages[:2]):
            logger.info(f"Sample Page {i+1} beginning: {repr(page.page_content[:150])}...")
            
        # 3. Split the cleaned pages into chunks
        chunks = split_documents(pages)
        logger.info(f"Verification: Created {len(chunks)} chunks.")
        if chunks:
            logger.info(f"First chunk text sample:\n{chunks[0].page_content[:300]}...\n")
            logger.info(f"First chunk metadata: {chunks[0].metadata}")
            
        # 4. Verify Database Writes & Reads
        logger.info("Verification: Writing mock topic metadata to SQLite...")
        save_topic_metadata(
            topic_id="pocso",
            title="POCSO Act, 2012",
            summary="This is a verified mock summary of child protections under the POCSO Act.",
            key_rights=["Right to safety", "Right to child-friendly recording environment"],
            penalties=["Imprisonment up to 20 years for penetrative assault"],
            card_description="Protects children from sexual abuse and exploitation.",
            source_url="https://www.indiacode.nic.in/handle/123456789/1987"
        )
        
        logger.info("Verification: Retrieving metadata from SQLite...")
        retrieved = get_topic_metadata("pocso")
        if retrieved:
            logger.info(f"SUCCESS: Retrieved title: {retrieved['title']}")
            logger.info(f"SUCCESS: Retrieved summary: {retrieved['summary']}")
            logger.info(f"SUCCESS: Retrieved rights: {retrieved['key_rights']}")
        else:
            logger.error("FAILURE: Metadata retrieval returned None.")
            sys.exit(1)
            
        logger.info("=== Pipeline Phase 2 Verification Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"Verification script failed with exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_verification()

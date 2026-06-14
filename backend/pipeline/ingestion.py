import os
from typing import Dict, Any
from core.config import settings
from core.logging_config import logger
from pipeline.loader import load_and_clean_pdf
from pipeline.splitter import split_documents
from storage.database import init_db, save_topic_metadata, clear_db
from storage.vector_store import add_documents_to_store
from chains.metadata_chain import build_metadata_chain

LEGAL_SOURCES: Dict[str, Dict[str, Any]] = {
    "pocso": {
        "name": "POCSO Act, 2012",
        "description": "Protects children from sexual abuse and exploitation.",
        "filename": "pocso.pdf",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/2079"
    },
    "consumer": {
        "name": "Consumer Protection Act, 2019",
        "description": "Protects consumer rights and prevents unfair trade practices.",
        "filename": "consumer_protection.pdf",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/15256"
    },
    "cyber": {
        "name": "IT Act (Cyber Law), 2000",
        "description": "Defines legal frameworks for electronic commerce and cyber offenses.",
        "filename": "cyber_crime.pdf",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/13116"
    },
    "rti": {
        "name": "Right to Information Act, 2005",
        "description": "Empowers citizens to request information from public authorities.",
        "filename": "rti.pdf",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/2065"
    },
    "gst": {
        "name": "GST Registration Regulations",
        "description": "Framework and procedures for Goods and Services Tax registration.",
        "filename": "gst_registration.pdf",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/2643"
    }
}

def ingest_all_topics():
    logger.info("Starting ingestion orchestrator...")
    init_db()
    clear_db()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sources_dir = os.path.join(base_dir, "data", "sources")
    
    # Initialize the combined metadata chain
    metadata_chain = build_metadata_chain()
    
    for topic_id, meta in LEGAL_SOURCES.items():
        pdf_path = os.path.join(sources_dir, meta["filename"])
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF source for '{topic_id}' not found at {pdf_path}. Skipping.")
            continue
            
        logger.info(f"Ingesting topic: {meta['name']}")
        try:
            # 1. Load and clean official PDF pages
            pages = load_and_clean_pdf(pdf_path)
            
            # 2. Split documents into chunks
            chunks = split_documents(pages)
            logger.info(f"Generated {len(chunks)} chunks for {topic_id}.")
            
            # Tag metadata specifically for Qdrant payload filtering
            for chunk in chunks:
                chunk.metadata["topic_id"] = topic_id
            
            # 3. Add to Qdrant Vector Store
            add_documents_to_store(chunks)
            
            # 4. Generate LLM summaries & extractions in a single call
            representative_text = "\n\n".join([page.page_content for page in pages])
            logger.info(f"Generating combined summary, rights, and penalties for '{topic_id}' using Gemini (1 Call)...")
            metadata = metadata_chain.invoke({"text": representative_text})
            
            # 5. Create SQLite metadata cache entry
            save_topic_metadata(
                topic_id=topic_id,
                title=meta["name"],
                summary=metadata.summary,
                key_rights=metadata.rights,
                penalties=metadata.penalties,
                card_description=meta["description"],
                source_url=meta["source_url"]
            )
            logger.info(f"Successfully finished ingestion of {topic_id}.")
            
        except Exception as e:
            logger.error(f"Error during ingestion of {topic_id}: {e}", exc_info=True)

if __name__ == "__main__":
    ingest_all_topics()

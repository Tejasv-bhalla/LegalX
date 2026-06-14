import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.loader import load_and_clean_pdf
from storage.database import init_db, save_topic_metadata, clear_db
from chains.metadata_chain import build_metadata_chain
from core.logging_config import logger

LEGAL_SOURCES = {
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

def update_metadata_only():
    logger.info("Starting SQLite-only metadata update...")
    init_db()
    clear_db()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sources_dir = os.path.join(base_dir, "data", "sources")
    metadata_chain = build_metadata_chain()
    
    for topic_id, meta in LEGAL_SOURCES.items():
        pdf_path = os.path.join(sources_dir, meta["filename"])
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF source for '{topic_id}' not found at {pdf_path}. Skipping.")
            continue
            
        logger.info(f"Extracting and generating metadata for topic: {meta['name']}")
        try:
            # 1. Load PDF pages to build representative text
            pages = load_and_clean_pdf(pdf_path)
            representative_text = "\n\n".join([page.page_content for page in pages])
            
            # 2. Invoke Gemini 2.5 Flash metadata extraction (max_output_tokens has been increased to 4096 in llm.py)
            logger.info(f"Calling Gemini for '{topic_id}' metadata...")
            metadata = metadata_chain.invoke({"text": representative_text})
            
            # 3. Save to SQLite cache
            save_topic_metadata(
                topic_id=topic_id,
                title=meta["name"],
                summary=metadata.summary,
                key_rights=metadata.rights,
                penalties=metadata.penalties,
                card_description=meta["description"],
                source_url=meta["source_url"]
            )
            logger.info(f"Successfully updated metadata for {topic_id} in SQLite.")
            
        except Exception as e:
            logger.error(f"Failed to update metadata for {topic_id}: {e}", exc_info=True)

if __name__ == "__main__":
    update_metadata_only()

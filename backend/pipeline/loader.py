import os
import re
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from core.logging_config import logger

def clean_page_text(text: str) -> str:
    # 1. Strip standalone page numbers (e.g., "1", "12", "  3  " on their own lines)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    
    # 2. Strip common government header fragments that repeat
    # Examples: Running titles of the acts
    header_patterns = [
        r"THE PROTECTION OF CHILDREN FROM SEXUAL OFFENCES ACT, 2012",
        r"ARRANGEMENT OF SECTIONS",
        r"ARRANGEMENT OF CLAUSES"
    ]
    for pattern in header_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
    return text.strip()

def load_and_clean_pdf(filepath: str) -> List[Document]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source PDF not found at {filepath}")
        
    logger.info(f"Loading PDF from {filepath}...")
    loader = PyPDFLoader(filepath)
    raw_pages = loader.load()
    
    cleaned_pages = []
    logger.info(f"Loaded {len(raw_pages)} pages. Cleaning content...")
    
    for page in raw_pages:
        # Check if the page is a Table of Contents page
        text = page.page_content
        if "ARRANGEMENT OF SECTIONS" in text or "ARRANGEMENT OF CLAUSES" in text:
            logger.info(f"Skipping Table of Contents page (page number {page.metadata.get('page', 0) + 1})")
            continue
            
        # Clean page content
        cleaned_text = clean_page_text(text)
        if not cleaned_text:
            continue
            
        page.page_content = cleaned_text
        # Ensure metadata is clean and present
        page.metadata["source_file"] = os.path.basename(filepath)
        cleaned_pages.append(page)
        
    logger.info(f"Cleaning complete. Retained {len(cleaned_pages)} content pages.")
    return cleaned_pages

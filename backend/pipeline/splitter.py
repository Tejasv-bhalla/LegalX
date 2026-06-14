from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.logging_config import logger

def split_documents(docs: List[Document]) -> List[Document]:
    # Configure text splitter optimized for legal text clauses
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    logger.info(f"Splitting {len(docs)} documents into chunks...")
    chunks = splitter.split_documents(docs)
    logger.info(f"Generated {len(chunks)} overlapping text chunks.")
    
    # Clean chunk metadata structure
    for i, chunk in enumerate(chunks):
        # Retain original source information and add a unique chunk index
        chunk.metadata["chunk_index"] = i
        
    return chunks

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.loader import load_and_clean_pdf
from chains.metadata_chain import build_metadata_chain
from core.config import settings

def debug_ingestion():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "data", "sources", "pocso.pdf")
    pages = load_and_clean_pdf(pdf_path)
    representative_text = "\n\n".join([page.page_content for page in pages])
    
    print(f"Loaded {len(pages)} pages. Total length: {len(representative_text)} chars.")
    
    metadata_chain = build_metadata_chain()
    print("Calling Gemini...")
    metadata = metadata_chain.invoke({"text": representative_text})
    
    print("\n--- LLM OUTPUT SUMMARY ---")
    print(metadata.summary)
    print("\n--- RIGHTS ---")
    print(metadata.rights)
    print("\n--- PENALTIES ---")
    print(metadata.penalties)

if __name__ == "__main__":
    debug_ingestion()

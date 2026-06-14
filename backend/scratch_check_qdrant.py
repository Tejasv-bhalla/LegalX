import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from core.config import settings

def check_qdrant():
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    collection_name = settings.qdrant_collection
    
    print(f"Checking Qdrant collection: {collection_name}...")
    try:
        info = client.get_collection(collection_name)
        print("Collection Status:", info.status)
        count_res = client.count(collection_name)
        print("Points Count (Count API):", count_res.count)
        
        # Scroll some points to inspect payload structure
        response = client.scroll(
            collection_name=collection_name,
            limit=3,
            with_payload=True,
            with_vectors=False
        )
        points = response[0]
        print("\n--- SAMPLE POINTS PAYLOADS ---")
        for i, point in enumerate(points):
            print(f"\nPoint {i+1} (ID: {point.id}):")
            print("Payload keys:", list(point.payload.keys()))
            metadata_dict = point.payload.get("metadata", {})
            print("metadata content:", metadata_dict)
            print("topic_id in metadata:", metadata_dict.get("topic_id"))
            print("page:", metadata_dict.get("page"))
            print("source_file:", metadata_dict.get("source_file"))
            print("text snippet:", point.payload.get("page_content", "")[:100] + "...")
            
    except Exception as e:
        print("Failed to query Qdrant:", e)

if __name__ == "__main__":
    check_qdrant()

from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from core.config import settings
from core.logging_config import logger

# Thread-safe singleton holder for embeddings
_embeddings_instance = None

def get_embedding_model() -> HuggingFaceEmbeddings:
    global _embeddings_instance
    if _embeddings_instance is None:
        logger.info("Initializing HuggingFaceEmbeddings with BAAI/bge-small-en-v1.5...")
        # BGE-small-en-v1.5 is 384 dimensions
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        logger.info("Embedding model loaded successfully.")
    return _embeddings_instance

def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key
    )

def init_vector_store() -> QdrantVectorStore:
    client = get_qdrant_client()
    collection_name = settings.qdrant_collection
    
    # Check if collection exists, create if not
    try:
        if not client.collection_exists(collection_name):
            logger.info(f"Collection '{collection_name}' does not exist. Creating...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=384,  # bge-small output dimensions
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Collection '{collection_name}' created successfully.")
    except Exception as e:
        logger.error(f"Failed to verify/create Qdrant collection: {e}")
        raise e
        
    embeddings = get_embedding_model()
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings
    )

def add_documents_to_store(chunks: List[Document]):
    if not chunks:
        logger.warning("No chunks provided to upload to Qdrant.")
        return
        
    logger.info(f"Uploading {len(chunks)} chunks to Qdrant...")
    vector_store = init_vector_store()
    
    # LangChain's QdrantVectorStore handles batch embedding and upsert
    vector_store.add_documents(chunks)
    logger.info("Chunks uploaded to Qdrant successfully.")

def search_vector_store(query: str, topic_id: str, k: int = 5) -> List[Document]:
    logger.info(f"Searching vector store for query: '{query}' (scoped to topic: '{topic_id}')...")
    vector_store = init_vector_store()
    
    # BGE recommendation: prefix search queries with this instruction
    prefixed_query = f"Represent this sentence for searching relevant passages: {query}"
    
    # Construct metadata filter for payload filtering
    payload_filter = Filter(
        must=[
            FieldCondition(
                key="metadata.topic_id",
                match=MatchValue(value=topic_id)
            )
        ]
    )
    
    # Retrieve top k documents using similarity search with the filter
    results = vector_store.similarity_search(
        query=prefixed_query,
        k=k,
        filter=payload_filter
    )
    
    logger.info(f"Retrieved {len(results)} chunks from Qdrant.")
    return results

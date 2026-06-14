from typing import List
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from core.config import settings
from core.logging_config import logger

# Thread-safe singleton holder for embeddings
_embeddings_instance = None

def get_embedding_model():
    global _embeddings_instance
    if _embeddings_instance is None:
        logger.info("Initializing lightweight FastEmbedEmbeddings with BAAI/bge-small-en-v1.5...")
        from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
        # FastEmbed is extremely low memory and runs BGE-small-en-v1.5 (384 dimensions)
        _embeddings_instance = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )
        logger.info("FastEmbed embedding model loaded successfully.")
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
    logger.info(f"Searching vector store for query: '{query}' (scoped to topic: '{topic_id}') using MMR...")
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
    
    # Retrieve top k documents using MMR search to ensure diverse sections are fetched
    results = vector_store.max_marginal_relevance_search(
        query=prefixed_query,
        k=k,
        fetch_k=12,         # Fetch 12 candidates first
        filter=payload_filter,
        lambda_mult=0.65    # Balance relevance vs diversity (0.65 is optimal for legal context)
    )
    
    logger.info(f"Retrieved {len(results)} chunks from Qdrant using MMR.")
    return results

import time
from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse
from storage.vector_store import search_vector_store
from storage.database import get_topic_metadata
from chains.rag_chain import build_rag_chain
from core.logging_config import logger
from core.exceptions import LLMRateLimitException, ServiceUnavailableException

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Initialize RAG chain once
try:
    rag_chain = build_rag_chain()
except Exception as e:
    logger.error(f"Failed to initialize RAG chain: {e}")
    rag_chain = None

@router.post("", response_model=ChatResponse)
async def chat_with_law(request: ChatRequest):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG system is not initialized")
        
    logger.info(f"Received chat request for topic: {request.topic_id}")
    
    # Try retrieving relevant chunks from Qdrant Cloud
    is_fallback = False
    citations = []
    context_blocks = []
    
    start_search = time.time()
    try:
        results = search_vector_store(
            query=request.question,
            topic_id=request.topic_id,
            k=5
        )
        logger.info(f"Vector store search took {time.time() - start_search:.4f} seconds.")
        
        for doc in results:
            page_num = doc.metadata.get("page", 0) + 1
            filename = doc.metadata.get("source_file", "Official Document")
            citation_str = f"{filename} (Page {page_num})"
            if citation_str not in citations:
                citations.append(citation_str)
                
            context_blocks.append(f"[Source: {citation_str}]\n{doc.page_content}")
            
    except Exception as qdrant_exc:
        logger.error(f"Qdrant vector retrieval failed after {time.time() - start_search:.4f}s, triggering SQLite fallback: {qdrant_exc}")
        is_fallback = True
        # Fetch overview summary from local SQLite
        topic_meta = get_topic_metadata(request.topic_id)
        if topic_meta and topic_meta.get("summary"):
            context_blocks.append(f"[Local Summary Cache]\n{topic_meta['summary']}")
            citations.append("Local Summary Cache")
        else:
            raise ServiceUnavailableException("Our vector search and local summary databases are both offline.")

    context = "\n\n---\n\n".join(context_blocks)
    
    try:
        logger.info("Invoking LLM RAG Q&A chain...")
        start_llm = time.time()
        answer = await rag_chain.ainvoke({
            "context": context if context else "No relevant context found.",
            "question": request.question
        })
        logger.info(f"LLM generation took {time.time() - start_llm:.4f} seconds.")
        
        # Prepend a warning message if serving from fallback
        if is_fallback:
            answer = (
                "⚠️ **Service Notice**: The vector database is currently offline. "
                "I have answered using the general cached summary of this Act:\n\n" + answer
            )
            
        # If no context was retrieved (and not in fallback), return the safe message
        if not context_blocks and not is_fallback:
            answer = "I am sorry, but the provided official documents do not contain information to answer that question."
            
        return ChatResponse(
            answer=answer,
            sources=citations,
            topic_id=request.topic_id
        )
        
    except Exception as e:
        logger.error(f"Error occurred during LLM execution: {e}", exc_info=True)
        # Capture API rate limit limits or other service errors
        err_msg = str(e)
        if "ResourceExhausted" in err_msg or "429" in err_msg or "rate_limit" in err_msg.lower():
            raise LLMRateLimitException()
        raise HTTPException(status_code=500, detail="Internal AI reasoning error. Please retry.")

from fastapi.responses import StreamingResponse
import json

async def generate_chat_stream(request: ChatRequest):
    if not rag_chain:
        yield f"data: {json.dumps({'type': 'error', 'detail': 'RAG system is not initialized'})}\n\n"
        return
        
    logger.info(f"Received streaming chat request for topic: {request.topic_id}")
    
    # Try retrieving relevant chunks from Qdrant Cloud
    is_fallback = False
    citations = []
    context_blocks = []
    
    start_search = time.time()
    try:
        results = search_vector_store(
            query=request.question,
            topic_id=request.topic_id,
            k=5
        )
        logger.info(f"Streaming vector store search took {time.time() - start_search:.4f} seconds.")
        
        for doc in results:
            page_num = doc.metadata.get("page", 0) + 1
            filename = doc.metadata.get("source_file", "Official Document")
            citation_str = f"{filename} (Page {page_num})"
            if citation_str not in citations:
                citations.append(citation_str)
                
            context_blocks.append(f"[Source: {citation_str}]\n{doc.page_content}")
            
    except Exception as qdrant_exc:
        logger.error(f"Qdrant vector retrieval failed for streaming request after {time.time() - start_search:.4f}s, triggering SQLite fallback: {qdrant_exc}")
        is_fallback = True
        # Fetch overview summary from local SQLite
        topic_meta = get_topic_metadata(request.topic_id)
        if topic_meta and topic_meta.get("summary"):
            context_blocks.append(f"[Local Summary Cache]\n{topic_meta['summary']}")
            citations.append("Local Summary Cache")
        else:
            yield f"data: {json.dumps({'type': 'error', 'detail': 'Our search databases are both offline.'})}\n\n"
            return

    # Yield citations/sources event first
    yield f"data: {json.dumps({'type': 'sources', 'sources': citations})}\n\n"
    
    # If fallback is active, yield the fallback notice token first
    if is_fallback:
        fallback_notice = (
            "⚠️ **Service Notice**: The vector database is currently offline. "
            "I have answered using the general cached summary of this Act:\n\n"
        )
        yield f"data: {json.dumps({'type': 'token', 'token': fallback_notice})}\n\n"

    # If no context was retrieved (and not in fallback), return the safe message
    if not context_blocks and not is_fallback:
        no_context_msg = "I am sorry, but the provided official documents do not contain information to answer that question."
        yield f"data: {json.dumps({'type': 'token', 'token': no_context_msg})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return

    context = "\n\n---\n\n".join(context_blocks)
    
    try:
        logger.info("Invoking streaming LLM RAG Q&A chain...")
        start_llm = time.time()
        async for token in rag_chain.astream({
            "context": context,
            "question": request.question
        }):
            yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
        logger.info(f"Streaming LLM generation completed in {time.time() - start_llm:.4f} seconds.")
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error occurred during streaming LLM execution: {e}", exc_info=True)
        err_msg = str(e)
        detail = "Internal AI reasoning error. Please retry."
        if "ResourceExhausted" in err_msg or "429" in err_msg or "rate_limit" in err_msg.lower():
            detail = "Our AI reasoning capacity is currently busy. Please wait a few moments and try again."
        yield f"data: {json.dumps({'type': 'error', 'detail': detail})}\n\n"

@router.post("/stream")
async def chat_with_law_stream(request: ChatRequest):
    return StreamingResponse(
        generate_chat_stream(request),
        media_type="text/event-stream"
    )


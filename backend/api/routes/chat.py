from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse
from storage.vector_store import search_vector_store
from chains.rag_chain import build_rag_chain
from core.logging_config import logger

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
    try:
        # 1. Retrieve relevant chunks from Qdrant Cloud scoped to the topic_id
        results = search_vector_store(
            query=request.question,
            topic_id=request.topic_id,
            k=5
        )
        
        # 2. Extract citations (collect unique page labels/numbers)
        citations = []
        context_blocks = []
        
        for doc in results:
            page_num = doc.metadata.get("page", 0) + 1
            filename = doc.metadata.get("source_file", "Official Document")
            citation_str = f"{filename} (Page {page_num})"
            if citation_str not in citations:
                citations.append(citation_str)
                
            context_blocks.append(f"[Source: {citation_str}]\n{doc.page_content}")
            
        context = "\n\n---\n\n".join(context_blocks)
        
        # 3. Call the RAG chain
        logger.info("Invoking Gemini RAG Q&A chain...")
        answer = await rag_chain.ainvoke({
            "context": context if context else "No relevant context found.",
            "question": request.question
        })
        
        # If no context was retrieved, return the standard safe fallback message
        if not results:
            answer = "I am sorry, but the provided official documents do not contain information to answer that question."
            
        return ChatResponse(
            answer=answer,
            sources=citations,
            topic_id=request.topic_id
        )
        
    except Exception as e:
        logger.error(f"Error occurred during RAG chat execution: {e}", exc_info=True)
        # Capture API rate limit limits or other service errors
        if "ResourceExhausted" in str(e) or "429" in str(e):
            raise HTTPException(
                status_code=429, 
                detail="Our AI query capacity is currently full. Please try again in a few moments."
            )
        raise HTTPException(status_code=500, detail="Internal AI reasoning error. Please retry.")

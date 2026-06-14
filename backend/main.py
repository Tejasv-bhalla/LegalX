import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logging_config import logger
from storage.vector_store import get_embedding_model, init_vector_store
from storage.database import init_db
from api.routes import topics, chat, audio

app = FastAPI(
    title="LegalX AI Knowledge Centre",
    description="Production-grade FastAPI backend service for layman legal assistant",
    version="2.0.0"
)

# Configure CORS middleware
origins = [
    "http://localhost:5173",  # Vite local development
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Register route routers
app.include_router(topics.router)
app.include_router(chat.router)
app.include_router(audio.router)

@app.on_event("startup")
def startup_event():
    logger.info("Starting up LegalX API Server...")
    
    # 1. Initialize local database tables
    try:
        init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database during startup: {e}")
        
    # 2. Pre-load/warm up the local BGE embedding model into memory
    # This avoids cold-start delays on the first API request.
    try:
        get_embedding_model()
        init_vector_store()
        logger.info("Startup warmup complete. Server is ready.")
    except Exception as e:
        logger.critical(f"Warmup failed. Embedding model or Qdrant cluster is offline: {e}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

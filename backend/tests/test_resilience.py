import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chat_rate_limit_exception_handling():
    """Verify that catching an LLM rate limit exception yields HTTP 429 response."""
    # Mock search_vector_store to succeed, and mock rag_chain invocation to throw a rate limit error
    with patch("api.routes.chat.search_vector_store") as mock_search, \
         patch("api.routes.chat.rag_chain") as mock_chain:
         
        mock_search.return_value = []
        
        # Mock rag_chain.ainvoke to raise an exception indicating rate limit
        mock_chain.ainvoke = MagicMock(side_effect=Exception("ResourceExhausted: 429 Too Many Requests"))
        
        response = client.post(
            "/api/chat",
            json={"topic_id": "pocso", "question": "What are the penalties?"}
        )
        
        assert response.status_code == 429
        assert "AI reasoning capacity is currently busy" in response.json()["detail"]

def test_chat_qdrant_offline_sqlite_fallback():
    """Verify that when Qdrant is offline, the chat endpoint falls back to the SQLite summary."""
    with patch("api.routes.chat.search_vector_store", side_effect=Exception("Qdrant connection timeout")), \
         patch("api.routes.chat.get_topic_metadata") as mock_get_db, \
         patch("api.routes.chat.rag_chain") as mock_chain:
         
        # Mock SQLite to return valid cached topic metadata
        mock_get_db.return_value = {
            "summary": "This is the cached plain-English summary of POCSO.",
            "key_rights": [],
            "penalties": []
        }
        
        # Mock LLM as an async function
        mock_chain.ainvoke = AsyncMock(return_value="Mocked answer using local summary context.")
        
        response = client.post(
            "/api/chat",
            json={"topic_id": "pocso", "question": "What is the age limit?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Service Notice" in data["answer"]
        assert "Local Summary Cache" in data["sources"]
        
        # Verify LLM was invoked with the SQLite summary content
        args, kwargs = mock_chain.ainvoke.call_args
        assert "[Local Summary Cache]" in args[0]["context"]
        assert "This is the cached plain-English summary of POCSO." in args[0]["context"]

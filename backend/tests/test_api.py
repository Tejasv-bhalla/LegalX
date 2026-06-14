import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

# Mock database responses
MOCK_TOPICS = [
    {"id": "pocso", "title": "POCSO Act", "card_description": "Protection of children", "source_url": "https://example.com/pocso"},
    {"id": "cyber_crime", "title": "Information Technology Act", "card_description": "Cyber security laws", "source_url": "https://example.com/it"}
]

MOCK_TOPIC_DETAIL = {
    "id": "pocso",
    "title": "POCSO Act",
    "summary": "This is a plain English summary of the POCSO Act.",
    "key_rights": ["Right to confidentiality", "Right to support"],
    "penalties": ["Imprisonment up to life"],
    "card_description": "Protection of children",
    "source_url": "https://example.com/pocso"
}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("api.routes.topics.get_all_topics")
def test_list_topics(mock_get_all, client):
    mock_get_all.return_value = MOCK_TOPICS
    response = client.get("/api/topics")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == "pocso"

@patch("api.routes.topics.get_topic_metadata")
def test_get_topic_detail(mock_get_meta, client):
    mock_get_meta.return_value = MOCK_TOPIC_DETAIL
    response = client.get("/api/topics/pocso")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "pocso"
    assert data["key_rights"] == ["Right to confidentiality", "Right to support"]
    assert "summary" in data

@patch("api.routes.topics.get_topic_metadata")
def test_get_topic_detail_not_found(mock_get_meta, client):
    mock_get_meta.return_value = None
    response = client.get("/api/topics/unknown_topic")
    assert response.status_code == 404

def test_chat_invalid_payload(client):
    # Missing parameters
    response = client.post("/api/chat", json={"topic_id": "pocso"})
    assert response.status_code == 422

@patch("api.routes.chat.search_vector_store")
@patch("api.routes.chat.rag_chain")
def test_chat_success(mock_rag, mock_search, client):
    # Mock vector store search
    mock_doc = MagicMock()
    mock_doc.page_content = "Under POCSO section 4, penetrative sexual assault has a penalty."
    mock_doc.metadata = {"page": 3, "source_file": "pocso.pdf"}
    mock_search.return_value = [mock_doc]

    # Mock RAG chain invoke
    mock_rag.ainvoke = AsyncMock(return_value="The penalty under POCSO is life imprisonment.")

    payload = {"topic_id": "pocso", "question": "What is the penalty?"}
    response = client.post("/api/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "penalty under POCSO" in data["answer"]
    assert len(data["sources"]) == 1
    assert "pocso.pdf" in data["sources"][0]

@patch("api.routes.audio.get_topic_metadata")
@patch("api.routes.audio.generate_speech_file")
def test_get_audio_success(mock_gen_file, mock_get_meta, client, tmp_path):
    mock_get_meta.return_value = MOCK_TOPIC_DETAIL
    
    # Create a dummy audio file in tmp_path
    dummy_file = tmp_path / "pocso.mp3"
    dummy_file.write_bytes(b"dummy mp3 data")
    mock_gen_file.return_value = dummy_file

    response = client.get("/api/audio/pocso")
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"dummy mp3 data"

@patch("api.routes.chat.search_vector_store")
@patch("api.routes.chat.rag_chain")
def test_chat_stream_success(mock_rag, mock_search, client):
    # Mock vector store search
    mock_doc = MagicMock()
    mock_doc.page_content = "Under POCSO section 4, penetrative sexual assault has a penalty."
    mock_doc.metadata = {"page": 3, "source_file": "pocso.pdf"}
    mock_search.return_value = [mock_doc]

    # Mock rag_chain.astream to yield tokens
    async def mock_astream(*args, **kwargs):
        yield "The penalty "
        yield "under POCSO "
        yield "is life imprisonment."
        
    mock_rag.astream = mock_astream

    payload = {"topic_id": "pocso", "question": "What is the penalty?"}
    response = client.post("/api/chat/stream", json=payload)
    
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    
    # Read response body chunks
    body = response.content.decode("utf-8")
    lines = body.split("\n\n")
    
    # Check that it yielded sources first, then tokens, and finally done
    assert any("sources" in line and "pocso.pdf" in line for line in lines)
    assert any("token" in line and "The penalty " in line for line in lines)
    assert any("done" in line for line in lines)


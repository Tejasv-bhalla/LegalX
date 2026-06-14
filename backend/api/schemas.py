from pydantic import BaseModel, Field
from typing import List, Optional

class TopicOverview(BaseModel):
    id: str = Field(description="Unique string identifier of the topic (e.g. 'pocso')")
    title: str = Field(description="Clean, official name of the legal Act")
    card_description: str = Field(description="Short 1-2 sentence overview for card grids")
    source_url: str = Field(description="Official URL for landing page validation")

class TopicDetail(BaseModel):
    id: str = Field(description="Unique string identifier of the topic")
    title: str = Field(description="Official name of the legal Act")
    summary: str = Field(description="Plain-English Markdown summary of the Act")
    key_rights: List[str] = Field(description="List of citizen rights under this Act")
    penalties: List[str] = Field(description="List of key penalties/punishments")
    card_description: str = Field(description="Short card description")
    source_url: str = Field(description="Official URL for landing page validation")

class ChatRequest(BaseModel):
    topic_id: str = Field(description="ID of the topic context to search (e.g. 'pocso')")
    question: str = Field(description="The natural language question asked by the user")

class ChatResponse(BaseModel):
    answer: str = Field(description="Plain-English markdown response from RAG")
    sources: List[str] = Field(description="List of specific sections/pages cited in the response")
    topic_id: str = Field(description="The topic context ID associated with the query")

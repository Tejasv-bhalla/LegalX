from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from chains.llm import get_ingestion_llm

class TopicMetadata(BaseModel):
    summary: str = Field(
        description="A plain-English summary of the legal Act. Empathize with the user, write clearly, use active voice, and break it down into 2-3 readable paragraphs. Keep it under 250 words total."
    )
    rights: List[str] = Field(
        default=[],
        description="Key citizen rights, safeguards, or protections guaranteed by this Act. Limit to a maximum of 5 high-impact bullet points, written in simple layman language. If none are found, return an empty list."
    )
    penalties: List[str] = Field(
        default=[],
        description="Specific offenses and their corresponding punishments/fines. Limit to a maximum of 5 items, stating the offense and the exact sentence clearly. If none are found, return an empty list."
    )

def build_metadata_chain():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert legal advocate who translates complex legislation into citizen-friendly summaries and lists of rights/penalties. "
            "Analyze the legal text and generate: \n"
            "1. A layman summary under 250 words.\n"
            "2. A list of key rights or protections (max 5).\n"
            "3. A list of key offenses and their punishments (max 5).\n\n"
            "Be concise, highly accurate, and structure your final response exactly matching the requested JSON format."
        ),
        ("human", "Generate metadata for this legal text:\n\n{text}")
    ])
    
    llm = get_ingestion_llm(temperature=0.15)
    # Enforce structured output matching the TopicMetadata schema
    structured_llm = llm.with_structured_output(TopicMetadata)
    return prompt | structured_llm

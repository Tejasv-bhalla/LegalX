from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from core.config import settings
from core.logging_config import logger

def get_ingestion_llm(temperature: float = 0.15) -> ChatGoogleGenerativeAI:
    logger.info(f"Initializing Ingestion LLM: ChatGoogleGenerativeAI model='{settings.ingestion_model_name}' (temp={temperature})...")
    llm = ChatGoogleGenerativeAI(
        model=settings.ingestion_model_name,
        temperature=temperature,
        google_api_key=settings.google_api_key,
        max_output_tokens=4096,
    )
    return llm.with_retry(stop_after_attempt=3)

def get_chat_llm(temperature: float = 0.2) -> ChatGroq:
    logger.info(f"Initializing Chat LLM: ChatGroq model='{settings.chat_model_name}' (temp={temperature})...")
    llm = ChatGroq(
        model=settings.chat_model_name,
        temperature=temperature,
        groq_api_key=settings.groq_api_key,
    )
    return llm.with_retry(stop_after_attempt=3)

import os
import re
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import edge_tts
from storage.database import get_topic_metadata
from core.logging_config import logger

router = APIRouter(prefix="/api/audio", tags=["Audio"])

# Local directory where audio files will be cached
AUDIO_CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "audio_cache"
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "en-IN-NeerjaNeural"

def clean_markdown_for_tts(text: str) -> str:
    """
    Remove common markdown symbols (asterisks, hashtags, links, bold markers)
    to make the text sound natural when read aloud by the TTS engine.
    """
    # Remove headings marker
    text = re.sub(r'#+\s+', '', text)
    # Remove bold/italic markers
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'_+', '', text)
    # Remove markdown links (keep text, remove URL)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove blockquote markers
    text = re.sub(r'^\s*>\s*', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Clean list markers
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    # Clean checkbox lists
    text = re.sub(r'\[[ xX]\]', '', text)
    return text.strip()

async def generate_speech_file(topic_id: str, text: str) -> Path:
    audio_path = AUDIO_CACHE_DIR / f"{topic_id}.mp3"
    
    # Return from cache if it exists
    if audio_path.exists() and audio_path.stat().st_size > 0:
        logger.info(f"Serving cached audio file for topic '{topic_id}'")
        return audio_path

    # Clean the text before speech generation
    cleaned_text = clean_markdown_for_tts(text)
    if not cleaned_text:
        raise ValueError("Summary content is empty after cleaning.")

    logger.info(f"Synthesizing speech for topic '{topic_id}' using voice {VOICE}...")
    communicate = edge_tts.Communicate(cleaned_text, VOICE)
    await communicate.save(str(audio_path))
    logger.info(f"Speech saved successfully to {audio_path}")
    return audio_path

@router.get("/{topic_id}")
async def get_topic_audio(topic_id: str):
    try:
        # 1. Fetch metadata from local sqlite
        metadata = get_topic_metadata(topic_id)
        if not metadata or not metadata.get("summary"):
            logger.warning(f"Topic or summary not found for audio generation: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic or summary not found")

        # 2. Generate/retrieve audio file
        audio_file = await generate_speech_file(topic_id, metadata["summary"])
        
        # 3. Serve the file Response
        return FileResponse(
            path=str(audio_file),
            media_type="audio/mpeg",
            filename=f"{topic_id}.mp3"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to generate or serve audio for '{topic_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate voice translation. Please try again."
        )

from fastapi import APIRouter, HTTPException
from typing import List
from api.schemas import TopicOverview, TopicDetail
from storage.database import get_all_topics, get_topic_metadata
from core.logging_config import logger

router = APIRouter(prefix="/api/topics", tags=["Topics"])

@router.get("", response_model=List[TopicOverview])
def list_topics():
    logger.info("Fetching all topic overviews from SQLite...")
    try:
        topics = get_all_topics()
        return topics
    except Exception as e:
        logger.error(f"Error fetching topics from database: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal database error")

@router.get("/{topic_id}", response_model=TopicDetail)
def get_topic(topic_id: str):
    logger.info(f"Fetching detailed metadata for topic '{topic_id}' from SQLite...")
    try:
        metadata = get_topic_metadata(topic_id)
        if not metadata:
            logger.warning(f"Topic '{topic_id}' not found in database.")
            raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")
        return metadata
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching topic details for '{topic_id}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal database error")

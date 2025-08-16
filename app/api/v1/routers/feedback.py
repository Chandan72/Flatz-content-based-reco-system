from datetime import datetime, UTC
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.db import SessionLocal
from app.core.models import Interaction, FeedbackLog

router = APIRouter()

class FeedbackRequest(BaseModel):
    user_id: int
    item_id: int
    feedback_type: str = Field(pattern="^(view|click|like|book|attend|dismiss)$")
    timestamp: Optional[datetime] = None

class FeedbackResponse(BaseModel):
    status: str
    message: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""@router.post("/feedback", response_model=FeedbackResponse)
def log_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    #Log user feedback events with upsert behavior
    try:
        ts = feedback.timestamp or datetime.now(UTC)
        
        # Check if interaction already exists
        existing = db.query(Interaction).filter(
            Interaction.user_id == feedback.user_id,
            Interaction.item_id == feedback.item_id,
            Interaction.interaction_type == feedback.feedback_type
        ).first()
        
        if existing:
            # Update existing interaction's timestamp
            existing.timestamp = ts
            message = f"Updated {feedback.feedback_type} for user {feedback.user_id}"
        else:
            # Create new interaction
            interaction = Interaction(
                user_id=feedback.user_id,
                item_id=feedback.item_id,
                interaction_type=feedback.feedback_type,
                timestamp=ts
            )
            db.add(interaction)
            message = f"Logged {feedback.feedback_type} for user {feedback.user_id}"
        
        db.commit()
        
        return FeedbackResponse(status="success", message=message)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log feedback: {str(e)}")"""
@router.post("/feedback")
def log_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    # 1. Log to feedback_logs (always insert, never deduplicate)
    feedback_log = FeedbackLog(
        user_id=feedback.user_id,
        item_id=feedback.item_id,
        feedback_type=feedback.feedback_type,
        timestamp=datetime.now(UTC)
    )
    db.add(feedback_log)
    db.commit()
    return FeedbackResponse(status="success")
    
    # 2. Update main interactions (upsert behavior)
    """existing = db.query(Interaction).filter(...).first()
    if existing:
        existing.timestamp = datetime.now(UTC)
    else:
        db.add(Interaction(...))
    
    db.commit()"""


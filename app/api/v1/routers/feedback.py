from datetime import datetime, UTC
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.models import Interaction

router = APIRouter()

class FeedbackRequest(BaseModel):
    user_id: int
    item_id: int
    feedback_type: str = Field(pattern="^(view|click|like|book|attend|dismiss)$")
    timestamp: datetime = None

class FeedbackResponse(BaseModel):
    status: str
    message: str = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/feedback", response_model=FeedbackResponse)
def log_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Log user feedback events (views, clicks, likes, bookings, dismissals).
    This data feeds back into popularity and future CF models.
    """
    try:
        # Use provided timestamp or current time
        ts = feedback.timestamp or datetime.now(UTC)
        
        # Create interaction record
        interaction = Interaction(
            user_id=feedback.user_id,
            item_id=feedback.item_id,
            interaction_type=feedback.feedback_type,
            timestamp=ts
        )
        
        db.add(interaction)
        db.commit()
        
        return FeedbackResponse(
            status="success", 
            message=f"Logged {feedback.feedback_type} for user {feedback.user_id}"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log feedback: {str(e)}")

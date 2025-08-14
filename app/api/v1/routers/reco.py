from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.models import Interaction, Item
from app.services.reco.generators.content import content_gen
from app.api.v1.schemas.reco import HomefeedResponse, Recommendation
from datetime import datetime, UTC

router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/homefeed", response_model=HomefeedResponse)
def homefeed(user_id: int = Query(...), db: Session = Depends(get_db)):
    # 1. Retrieve the user’s most recent interaction
    last = (
        db.query(Interaction)
          .filter(Interaction.user_id == user_id)
          .order_by(Interaction.timestamp.desc())
          .first()
    )

    if last:
        item = db.query(Item).get(last.item_id)
        query_text = f"{item.title}. {item.description} [{item.community}]"
    else:
        # Cold-start fallback
        query_text = "Community events and services"

    # 2. Get content-based candidates
    try:
        candidate_ids = content_gen.get_similar(query_text, top_k=20)
    except Exception:
        raise HTTPException(500, "Recommendation engine not ready")

    # 3. Build the response
    recs = []
    for idx, iid in enumerate(candidate_ids, start=1):
        itm = db.query(Item).get(iid)
        recs.append(Recommendation(
            item_id=iid,
            title=itm.title,
            reason=f"Similar to your recent interest",
            tags=["content-based"],
            timestamp=datetime.now(UTC)
            
        ))

    return HomefeedResponse(user_id=user_id, recommendations=recs)

    
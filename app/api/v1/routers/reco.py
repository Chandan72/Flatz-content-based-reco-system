from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.models import Interaction, Item ,User
from app.services.reco.generators.content import content_gen
from app.services.reco.candidate_service import candidate_service
from app.services.reco.feature_extractor import build_features
from app.services.reco.ranker import ranker
from app.services.reco.explanations import reason_for
from app.api.v1.schemas.reco import HomefeedResponse, Recommendation
from app.services.reco.policy import policy_filter
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
        base_item = db.query(Item).get(last.item_id)
        user_query_text = f"{base_item.title}. {base_item.description} [{base_item.community}]"
    else:
        # Cold-start fallback
        query_text = "Community events and services"

    candidates= candidate_service.get_candidates(db, user_id)
    if not candidates:
        candidates=candidate_service.get_candidates_for_cold_user(db, user_id)
    user=db.query(User).get(user_id)
    user_community= getattr(user, "block", None)
    candidates=policy_filter.apply_all_policies(user_community, candidates, db)

    # if still no candidates, return empty
    if not candidates:
        return HomefeedResponse(user_id=user_id, recommendations=[])
    
    # extract features for ranking
    feats= build_features(db, user_query_text, candidates)

    #rank candidates

    ranked= ranker.rank(feats, top_k=20)

    #build response with reasons
    now= datetime.now(UTC)
    recs =[]
    for r in ranked:
        recs.append(Recommendation(
            item_id=r["item_id"],
            title=r["title"],
            reason=reason_for(r),
            tags=r.get("sources", []),
            timestamp=now
        ))

    
    return HomefeedResponse(user_id=user_id, recommendations=recs)

    
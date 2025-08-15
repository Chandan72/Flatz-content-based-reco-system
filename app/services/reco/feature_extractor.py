from datetime import datetime, UTC
from typing import Dict, List
from sqlalchemy.orm import Session
from app.core.models import Item
from app.services.reco.generators.content import content_gen
import numpy as np

def build_features(db: Session, user_query_text: str, candidates: List[Dict]) -> List[Dict]:
    """Extract features for each candidate item"""
    now = datetime.now(UTC)
    result = []
    
    for c in candidates:
        item = db.query(Item).get(c["item_id"])
        if not item:
            continue
            
        # Calculate recency score - FIX TIMEZONE ISSUE HERE
        created = getattr(item, "created_at", None) or now
        
        # Normalize created to UTC-aware if it's naive
        if created.tzinfo is None:
            created_aware = created.replace(tzinfo=UTC)
        else:
            created_aware = created.astimezone(UTC)
            
        recency_days = max(0.0, (now - created_aware).total_seconds() / 86400.0)
        recency = 1.0 / (1.0 + recency_days)
        
        # Calculate content similarity (simplified)
        content_sim = 0.5  # Placeholder - you can enhance this
        if "content" in c.get("sources", []):
            content_sim = 0.8  # Higher if from content source
            
        result.append({
            "item_id": item.id,
            "title": item.title,
            "community": getattr(item, "community", ""),
            "sources": c.get("sources", []),
            "features": {
                "content_sim": content_sim,
                "recency": recency,
            }
        })
    
    return result

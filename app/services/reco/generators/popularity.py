
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.core.models import Interaction, Item

@dataclass
class PopularItem:
    item_id: int
    score: float

class PopularityCandidateGenerator:
    """
    Computes decayed popularity scores per item, optionally scoped by community.
    Cache in memory; refresh on startup or periodic cron.
    """

    def __init__(self, half_life_days: float = 7.0):
        self.half_life_days = half_life_days
        self.global_top: List[PopularItem] = []
        self.by_community: Dict[str, List[PopularItem]] = {}

    def _time_decay(self, days: float) -> float:
        # Exponential half-life decay: weight = 0.5 ** (days / half_life)
        return 0.5 ** (days / self.half_life_days)

    def refresh(self, db: Session, top_k: int = 200):
        """
        Build global and per-community popularity lists with decay.
        """
        now = datetime.now(UTC)
        

             

        # Join interactions with items to get item.community
        q = (
            db.query(
                Interaction.item_id,
                Item.community,
                Interaction.timestamp,
                Interaction.interaction_type,
            )
            .join(Item, Item.id == Interaction.item_id)
        )

        # Accumulate scores in Python for clarity
        global_scores: Dict[int, float] = {}
        comm_scores: Dict[str, Dict[int, float]] = {}

        # Basic interaction weights; adjust as needed
        itype_weight = {
            "view": 1.0,
            "click": 1.5,
            "like": 2.0,
            "book": 3.0,
            "attend": 3.0,
            "dismiss": -1.0,
        }

        for item_id, community, ts, itype in q:
            if ts is None:
                continue
            if ts.tzinfo is None:
                ts_aware=ts.replace(tzinfo=UTC)

            else:
                ts_aware = ts.astimezone(UTC)
            days =(now -ts_aware).total_seconds()/86400.0
            decay= self._time_decay(days)
            w = itype_weight.get(itype, 1.0)
            score = w * decay

            global_scores[item_id] = global_scores.get(item_id, 0.0) + score

            if community:
                comm_scores.setdefault(community, {})
                comm_scores[community][item_id] = comm_scores[community].get(item_id, 0.0) + score

        # Convert to sorted lists
        self.global_top = [
            PopularItem(i, s) for i, s in sorted(global_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        ]

        self.by_community = {}
        for comm, scores in comm_scores.items():
            top = [PopularItem(i, s) for i, s in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]]
            self.by_community[comm] = top

    def top_k_global(self, k: int = 20) -> List[int]:
        return [p.item_id for p in self.global_top[:k]]

    def top_k_by_community(self, community: str, k: int = 20) -> List[int]:
        if community in self.by_community:
            return [p.item_id for p in self.by_community[community][:k]]
        return self.top_k_global(k)  # fallback


# Singleton
pop_gen = PopularityCandidateGenerator()

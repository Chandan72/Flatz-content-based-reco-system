from __future__ import annotations
from typing import List, Dict, Set, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.models import Interaction, Item, User
from app.services.reco.generators.content import content_gen
from app.services.reco.generators.popularity import pop_gen
from app.services.reco.generators.collaborative import cf_generator
import logging

logger = logging.getLogger(__name__)

class CandidateService:
    """
    Fusion service that combines multiple recommendation sources:
    - Content-based (semantic similarity to user's recent items)  
    - Community popularity (trending in user's neighborhood)
    - Global popularity (trending everywhere as fallback)
    
    Returns a unified candidate pool with source tracking for explanations.
    """
    
    def __init__(self, 
                 recent_n: int = 3,           # How many recent items to analyze
                 k_content: int = 30,         # Max content-based candidates
                 k_pop_comm: int = 20,        # Max community popularity candidates  
                 k_pop_global: int = 15):     # Max global popularity candidates
        self.recent_n = recent_n
        self.k_content = k_content
        self.k_pop_comm = k_pop_comm
        self.k_pop_global = k_pop_global

    def _get_recent_user_items(self, db: Session, user_id: int) -> List[Item]:
        """
        Fetch the user's most recent interactions to understand their current interests.
        
        Why this matters:
        - Recent activity is the best signal for current preferences
        - We return Item objects (not just IDs) so we can build rich query text
        - Ordered by timestamp DESC to prioritize the most recent
        """
        interactions = (
            db.query(Interaction)
            .filter(Interaction.user_id == user_id)
            .order_by(desc(Interaction.timestamp))
            .limit(self.recent_n)
            .all()
        )
        
        # Get the actual items, filtering out any that might have been deleted
        items = []
        for interaction in interactions:
            item = db.query(Item).get(interaction.item_id)
            if item:
                items.append(item)
        
        return items

    def _get_content_candidates(self, db: Session, recent_items: List[Item]) -> Set[int]:
        """
        Generate content-based candidates using semantic similarity.
        
        How it works:
        1. Build a rich query text from user's recent items
        2. Use our pre-built FAISS index to find semantically similar items
        3. Return item IDs for the candidate pool
        
        Why we combine multiple recent items:
        - Single item might be an outlier
        - Multiple items give us broader understanding of user interests
        - We can weight more recent items more heavily
        """
        if not recent_items:
            return set()
        
        candidates = set()
        
        try:
            # Strategy: Use the most recent item as primary signal
            primary_item = recent_items[0]
            primary_query = f"{primary_item.title}. {primary_item.description} [{primary_item.community}]"
            
            # Get content-based recommendations
            similar_ids = content_gen.get_similar(primary_query, top_k=self.k_content)
            candidates.update(similar_ids)
            
            # Optional: If we have multiple recent items, blend their signals
            if len(recent_items) > 1:
                for item in recent_items[1:]:
                    query = f"{item.title}. {item.description} [{item.community}]"
                    # Get fewer candidates from secondary items to avoid over-weighting
                    secondary_ids = content_gen.get_similar(query, top_k=self.k_content // 2)
                    candidates.update(secondary_ids)
                    
        except Exception as e:
            logger.warning(f"Content-based candidate generation failed: {e}")
            # Graceful degradation - continue with other sources
        
        return candidates

    def _get_popularity_candidates(self, db: Session, user: User) -> tuple[Set[int], Set[int]]:
        """
        Get popularity-based candidates with community preference.
        
        Returns:
        - community_candidates: Popular in user's community/block
        - global_candidates: Popular globally (as fallback)
        
        Why two types:
        - Community popularity provides local relevance
        - Global popularity ensures we have enough candidates even in small communities
        - Helps with cold-start when user has no interaction history
        """
        community_candidates = set()
        global_candidates = set()
        
        try:
            # First, try to get community-specific popular items
            if user and hasattr(user, 'block') and user.block:
                comm_ids = pop_gen.top_k_by_community(user.block, self.k_pop_comm)
                community_candidates.update(comm_ids)
            
            # Always get some global popular items as backup
            global_ids = pop_gen.top_k_global(self.k_pop_global)
            global_candidates.update(global_ids)
            
        except Exception as e:
            logger.warning(f"Popularity candidate generation failed: {e}")
        
        return community_candidates, global_candidates

    def _remove_recent_interactions(self, candidates: Dict[int, Set[str]], 
                                   recent_items: List[Item]) -> Dict[int, Set[str]]:
        """
        Remove items the user recently interacted with to avoid immediate repetition.
        
        Why this matters:
        - Users don't want to see the same items again immediately
        - Increases diversity in the feed
        - Prevents stale recommendations
        """
        recent_ids = {item.id for item in recent_items}
        return {iid: sources for iid, sources in candidates.items() 
                if iid not in recent_ids}

    def get_candidates(self, db:Session, user_id: int) -> List[Dict]:
        """Main fusion method: combine all candidate sourcce into a inified pool."""
        logger.info(f"Generating candidates for user {user_id}")
        # track candidates by item_id and their sources
        candidate_pool: Dict[int, Set[str]] ={}

        # 1. Cet user context
        user= db.query(User).get(user_id)
        recent_items= self._get_recent_user_items(db, user_id)

        logger.info(f"User {user_id} has {len(recent_items)} recent interactions")

        # 2. Generate content-based candidates
        try:
            content_candidates= self._get_content_candidates(db, recent_items)
            for item_id in content_candidates:
                if item_id not in candidate_pool:
                    candidate_pool[item_id]= set()
                candidate_pool[item_id].add("content")
            logger.info(f" Added {len(content_candidates)} content-based candidates")
        except Exception as e:
            logger.warning(f"Content candidate generative failed: {e}")

        if recent_items and len(recent_items) >0:
            try:
                for item in recent_items[:2]:
                    cf_ids= cf_generator.get_similar_items(item.id, top_k=10)
                    for iid in cf_ids:
                        if iid not in candidate_pool:
                            candidate_pool[iid]=set()
                        candidate_pool[iid].add("cf")

                logger.info(f"Added CF candidates based on recent items")
            except Exception as e:
                logger.warning(f"CF candidates generation failed: {e}")
        # 3.Generate popularity-based candidates
        try:
            comm_candidates, global_candidates= self._get_popularity_candidates(db, user)
            for intem_id in comm_candidates:
                if item_id not in candidate_pool:
                    candidate_pool[item_id] =set()
                    
                candidate_pool[item_id].add("pop-comm")

            for item_id in global_candidates:
                if item_id not in candidate_pool:
                    candidate_pool[item_id] = set()
                candidate_pool[item_id].add("pop-global")
            logger.info(f"Added {len(comm_candidates)} community and {len(global_candidates)} global candidates")
        except Exception as e:
            logger.warning(f"Popularity candidate generation failed: {e}")

        # 4. Remove recently interacted items to increase diversity
        try:
            candidate_pool= self._remove_recent_interactions(candidate_pool, recent_items)
        except Exception as e:
            logger.warning(f"Recent interaction filtering failed: {e}")

        # 5. Clean any potential None values and convert to list format
        result=[]
        for item_id, sources in candidate_pool.items():
            if sources is None or not sources:
                sources = {"fallback"}
            
            result.append({
                "item_id": item_id,
                "sources": list(sources)
            })

        logger.info(f"Final candidate pool: {len(result)} items")
        return result







    def get_candidates_for_cold_user(self, db: Session, user_id: int) -> List[Dict]:
        """
        Special handling for users with no interaction history.
        
        Cold-start strategy:
        1. Use community popularity as primary signal
        2. Fall back to global popularity  
        3. Optionally use user profile data (age, preferences) if available
        
        This ensures new users get a sensible, engaging first experience.
        """
        logger.info(f"Generating cold-start candidates for user {user_id}")
        
        user = db.query(User).get(user_id)
        candidate_pool: Dict[int, Set[str]] = {}
        
        # Rely heavily on popularity for cold users
        comm_candidates, global_candidates = self._get_popularity_candidates(db, user)
        
        for item_id in comm_candidates:
            candidate_pool.setdefault(item_id, set()).add("pop-comm")
        
        for item_id in global_candidates:
            candidate_pool.setdefault(item_id, set()).add("pop-global")
        
        # Could add: demographic-based candidates, onboarding preferences, etc.
        
        return [
            {"item_id": item_id, "sources": list(sources)}
            for item_id, sources in candidate_pool.items()
        ]


# Singleton instance for dependency injection
candidate_service = CandidateService()

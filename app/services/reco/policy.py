from typing import List, Dict, Set
from collections import Counter
from sqlalchemy.orm import Session
from app.core.models import Item, Interaction, User
import logging

logger = logging.getLogger(__name__)

class PolicyFilter:
    """
    Policy and Safety Layer for FlatZ Recommendations
    
    Applies business rules and safety checks to ensure:
    - Community relevance and isolation
    - Content quality standards  
    - Creator diversity limits
    - User safety and experience
    """
    
    def __init__(self, 
                 max_items_per_community: int = 8,      # Prefer local content
                 creator_frequency_cap: int = 3,         # Max items from same creator
                 min_interaction_threshold: int = 2,     # Min engagement for quality
                 community_preference_ratio: float = 0.6): # % local vs global content
        
        self.max_items_per_community = max_items_per_community
        self.creator_frequency_cap = creator_frequency_cap  
        self.min_interaction_threshold = min_interaction_threshold
        self.community_preference_ratio = community_preference_ratio

    def apply_community_isolation(self, 
                                user_community: str, 
                                candidates: List[Dict],
                                db: Session) -> List[Dict]:
        """
        Enforce community preference while allowing spillover.
        
        Why: FlatZ residents should see local content first, but not be completely isolated.
        Business logic: 60% local, 40% can be from other communities.
        """
        if not user_community:
            logger.warning("User has no community - skipping community isolation")
            return candidates
        
        community_items = []
        other_community_items = []
        
        for candidate in candidates:
            item = db.query(Item).get(candidate["item_id"])
            if not item:
                continue
                
            if item.community == user_community:
                community_items.append(candidate)
            else:
                other_community_items.append(candidate)
        
        # Calculate target distribution
        total_target = min(len(candidates), self.max_items_per_community + 5)
        community_target = int(total_target * self.community_preference_ratio)
        other_target = total_target - community_target
        
        # Select items maintaining preference ratio
        result = community_items[:community_target]
        if len(result) < community_target:
            # Not enough local content - fill with others
            other_target += (community_target - len(result))
        
        result.extend(other_community_items[:other_target])
        
        logger.info(f"Community filter: {len(community_items)} local, {len(other_community_items)} other -> {len(result)} total")
        return result

    def apply_creator_frequency_cap(self, 
                                  candidates: List[Dict],
                                  db: Session) -> List[Dict]:
        """
        Limit items from the same creator/source to ensure diversity.
        
        Why: Prevents any single creator from dominating the feed.
        Implementation: Use item.community as proxy for "creator" in this demo.
        Production: Would use actual creator_id or content_source fields.
        """
        creator_counts = Counter()
        filtered = []
        
        for candidate in candidates:
            item = db.query(Item).get(candidate["item_id"])
            if not item:
                continue
                
            # Use community as creator proxy for this demo
            creator = item.community or "unknown"
            
            if creator_counts[creator] < self.creator_frequency_cap:
                filtered.append(candidate)
                creator_counts[creator] += 1
                logger.debug(f"Added item {item.id} from creator {creator} (count: {creator_counts[creator]})")
            else:
                logger.debug(f"Skipped item {item.id} - creator {creator} over limit ({self.creator_frequency_cap})")
        
        logger.info(f"Creator cap applied: {len(candidates)} -> {len(filtered)} items")
        return filtered

    def filter_low_quality_items(self, 
                                candidates: List[Dict],
                                db: Session) -> List[Dict]:
        """
        Remove items with very low engagement or suspicious activity.
        
        Why: Low-quality content hurts user experience and engagement.
        Metrics: Interaction count, positive vs negative feedback ratios.
        """
        filtered = []
        
        for candidate in candidates:
            item_id = candidate["item_id"]
            
            # Count total interactions
            interaction_count = (
                db.query(Interaction)
                .filter(Interaction.item_id == item_id)
                .count()
            )
            
            # Count positive vs negative interactions
            positive_interactions = (
                db.query(Interaction)
                .filter(Interaction.item_id == item_id)
                .filter(Interaction.interaction_type.in_(["like", "book", "attend"]))
                .count()
            )
            
            negative_interactions = (
                db.query(Interaction)
                .filter(Interaction.item_id == item_id)
                .filter(Interaction.interaction_type.in_(["dismiss"]))
                .count()
            )
            
            # Quality checks
            meets_threshold = interaction_count >= self.min_interaction_threshold
            has_positive_ratio = (positive_interactions >= negative_interactions) if negative_interactions > 0 else True
            
            if meets_threshold and has_positive_ratio:
                filtered.append(candidate)
                logger.debug(f"Item {item_id}: {interaction_count} interactions, {positive_interactions} positive - PASSED")
            else:
                logger.debug(f"Item {item_id}: {interaction_count} interactions, {positive_interactions} positive - FILTERED")
        
        logger.info(f"Quality filter: {len(candidates)} -> {len(filtered)} items")
        return filtered

    def apply_safety_checks(self, 
                          candidates: List[Dict],
                          db: Session) -> List[Dict]:
        """
        Additional safety checks for content appropriateness.
        
        Why: Ensure platform safety and user trust.
        Implementation: Basic checks - can be extended with ML models.
        """
        safe_candidates = []
        
        for candidate in candidates:
            item = db.query(Item).get(candidate["item_id"])
            if not item:
                continue
            
            # Basic safety checks (extend as needed)
            title_safe = self._is_content_safe(item.title or "")
            description_safe = self._is_content_safe(item.description or "")
            
            if title_safe and description_safe:
                safe_candidates.append(candidate)
            else:
                logger.warning(f"Filtered unsafe content: item {item.id}")
        
        logger.info(f"Safety filter: {len(candidates)} -> {len(safe_candidates)} items")
        return safe_candidates

    def _is_content_safe(self, text: str) -> bool:
        """
        Basic content safety check.
        Production: Replace with proper content moderation API/ML model.
        """
        unsafe_keywords = ['spam', 'scam', 'dangerous', 'illegal']
        text_lower = text.lower()
        return not any(keyword in text_lower for keyword in unsafe_keywords)

    def apply_all_policies(self, 
                          user_community: str,
                          candidates: List[Dict],
                          db: Session) -> List[Dict]:
        """
        Apply all policy filters in the correct order.
        
        Order matters:
        1. Safety checks first (remove harmful content)
        2. Quality filters (remove low-engagement items)  
        3. Creator caps (ensure diversity)
        4. Community isolation (local preference)
        """
        if not candidates:
            return candidates
            
        logger.info(f"Applying policies to {len(candidates)} candidates")
        
        # Step 1: Safety checks
        candidates = self.apply_safety_checks(candidates, db)
        
        # Step 2: Quality filtering  
        candidates = self.filter_low_quality_items(candidates, db)
        
        # Step 3: Creator diversity
        candidates = self.apply_creator_frequency_cap(candidates, db)
        
        # Step 4: Community preference
        candidates = self.apply_community_isolation(user_community, candidates, db)
        
        logger.info(f"Policy filtering complete: {len(candidates)} items remain")
        return candidates

# Singleton instance
policy_filter = PolicyFilter()

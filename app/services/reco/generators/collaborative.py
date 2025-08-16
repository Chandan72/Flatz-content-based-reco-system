from typing import List, Dict, Set
import numpy as np
from collections import defaultdict
from sqlalchemy.orm import Session
from app.core.models import Interaction, Item
import logging

logger = logging.getLogger(__name__)

class SimpleCollaborativeFilter:
    """
    Item-based collaborative filtering using cosine similarity.
    "Users who interacted with X also interacted with Y"
    """
    
    def __init__(self):
        self.item_similarity = {}  # item_id -> [(similar_item_id, score), ...]
        self.interaction_weights = {
            "view": 1.0, "click": 1.5, "like": 2.0, 
            "book": 3.0, "attend": 3.0, "dismiss": -0.5
        }
    
    def build_model(self, db: Session):
        """Build item-item similarity matrix from interactions"""
        logger.info("Building collaborative filtering model...")
        
        # 1. Build user-item interaction matrix
        user_items = defaultdict(dict)  # user_id -> {item_id: weight}
        
        interactions = db.query(Interaction).all()
        logger.info(f"Processing {len(interactions)} interactions for CF")
        
        for inter in interactions:
            weight = self.interaction_weights.get(inter.interaction_type, 1.0)
            if inter.user_id not in user_items:
                user_items[inter.user_id] = {}
            user_items[inter.user_id][inter.item_id] = user_items[inter.user_id].get(inter.item_id, 0) + weight
        
        # 2. Get unique items
        items = list(set(item_id for user_data in user_items.values() for item_id in user_data.keys()))
        logger.info(f"Computing similarities for {len(items)} items")
        
        # 3. Compute item-item cosine similarities
        for i, item1 in enumerate(items):
            self.item_similarity[item1] = []
            
            for item2 in items[i+1:]:  # Only compute upper triangle
                sim = self._cosine_similarity(item1, item2, user_items)
                if sim > 0.1:  # Only store meaningful similarities
                    self.item_similarity[item1].append((item2, sim))
                    # Symmetric similarity
                    if item2 not in self.item_similarity:
                        self.item_similarity[item2] = []
                    self.item_similarity[item2].append((item1, sim))
            
            # Sort by similarity score
            self.item_similarity[item1].sort(key=lambda x: x[1], reverse=True)
        
        logger.info("Collaborative filtering model built successfully")
    
    def _cosine_similarity(self, item1: int, item2: int, user_items: dict) -> float:
        """Compute cosine similarity between two items"""
        # Find users who interacted with both items
        users1 = set(uid for uid, items in user_items.items() if item1 in items)
        users2 = set(uid for uid, items in user_items.items() if item2 in items)
        common_users = users1.intersection(users2)
        
        if len(common_users) < 2:  # Need at least 2 common users
            return 0.0
        
        # Build vectors
        vec1, vec2 = [], []
        for uid in common_users:
            vec1.append(user_items[uid].get(item1, 0))
            vec2.append(user_items[uid].get(item2, 0))
        
        # Cosine similarity
        vec1, vec2 = np.array(vec1), np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm1, norm2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_similar_items(self, item_id: int, top_k: int = 10) -> List[int]:
        """Get items similar to the given item"""
        if item_id not in self.item_similarity:
            return []
        
        similar = self.item_similarity[item_id][:top_k]
        return [item_id for item_id, score in similar]

# Singleton
cf_generator = SimpleCollaborativeFilter()

"""from typing import List, Dict

class Ranker:
    #Simple weighted ranking based on features
    def __init__(self, w_content: float = 0.6, w_recency: float = 0.4):
        self.w_content = w_content
        self.w_recency = w_recency
    
    def rank(self, items: List[Dict], top_k: int = 20) -> List[Dict]:
        #Rank items by weighted feature score
        for item in items:
            features = item.get("features", {})
            score = (
                self.w_content * features.get("content_sim", 0.0) +
                self.w_recency * features.get("recency", 0.0)
            )
            item["score"] = score
        
        # Sort by score (highest first) and return top_k
        ranked = sorted(items, key=lambda x: x["score"], reverse=True)
        return ranked[:top_k]

ranker = Ranker()"""
from typing import List, Dict
import numpy as np

class EnhancedRanker:
    """
    Enhanced ranking with multiple feature types and weighted scoring
    """
    def __init__(self, 
                 w_content: float = 0.4,
                 w_recency: float = 0.25, 
                 w_popularity: float = 0.15,
                 w_community_match: float = 0.2):
        self.w_content = w_content
        self.w_recency = w_recency
        self.w_popularity = w_popularity
        self.w_community_match = w_community_match

    def _calculate_popularity_score(self, sources: List[str]) -> float:
        """Score based on popularity signals"""
        if "pop-comm" in sources:
            return 1.0  # Highest - local trending
        elif "pop-global" in sources:
            return 0.7  # Medium - global trending
        else:
            return 0.3  # Low - no popularity signal

    def _calculate_community_match_score(self, sources: List[str], user_community: str, item_community: str) -> float:
        """Score based on community matching"""
        if user_community and item_community == user_community:
            return 1.0  # Perfect match
        elif "pop-comm" in sources:
            return 0.6  # From community popularity
        else:
            return 0.3  # No community match

    def rank(self, items: List[Dict], user_community: str = None, top_k: int = 20) -> List[Dict]:
        """Enhanced ranking with multiple signals"""
        for item in items:
            features = item.get("features", {})
            sources = item.get("sources", [])
            
            # Individual feature scores
            content_score = features.get("content_sim", 0.0)
            recency_score = features.get("recency", 0.0)
            popularity_score = self._calculate_popularity_score(sources)
            community_score = self._calculate_community_match_score(
                sources, user_community, item.get("community")
            )
            
            # Weighted combination
            total_score = (
                self.w_content * content_score +
                self.w_recency * recency_score +
                self.w_popularity * popularity_score +
                self.w_community_match * community_score
            )
            
            item["score"] = total_score
            item["feature_breakdown"] = {
                "content": content_score,
                "recency": recency_score,
                "popularity": popularity_score,
                "community": community_score
            }
        
        # Sort and return top k
        ranked = sorted(items, key=lambda x: x["score"], reverse=True)
        return ranked[:top_k]

ranker = EnhancedRanker()


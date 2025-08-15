from typing import List, Dict

class Ranker:
    """Simple weighted ranking based on features"""
    def __init__(self, w_content: float = 0.6, w_recency: float = 0.4):
        self.w_content = w_content
        self.w_recency = w_recency
    
    def rank(self, items: List[Dict], top_k: int = 20) -> List[Dict]:
        """Rank items by weighted feature score"""
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

ranker = Ranker()

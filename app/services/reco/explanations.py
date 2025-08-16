from typing import Dict

def reason_for(item: Dict) -> str:
    """Generate explanation text based on item sources and features"""
    sources = set(item.get("sources", []))
    features = item.get("features", {})
    
    if "content" in sources:
        return "Similar to your recent interest"
    elif "cf" in sources:  
        return "People with similar tastes also liked this"
    elif "pop-comm" in sources:
        community = item.get("community", "your area")
        return f"Trending in {community}"
    elif features.get("recency", 0.0) > 0.6:
        return "New this week"
    elif "pop-global" in sources:
        return "Popular right now"
    else:
        return "Recommended for you"

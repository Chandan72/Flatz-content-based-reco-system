from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Recommendation(BaseModel):
    item_id: int
    title: Optional[str]
    reason: Optional[str]
    tags: Optional[List[str]]
    timestamp: Optional[datetime]

class HomefeedResponse(BaseModel):
    user_id: int
    recommendations: List[Recommendation]

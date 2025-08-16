from typing import Optional
import json
from redis.asyncio import Redis
from pydantic import BaseModel

class CacheConfig(BaseModel):
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

class CacheService:
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis: Optional[Redis] = None

    async def initialize(self):
        self.redis = Redis(
            host=self.config.REDIS_URL,
            password=self.config.REDIS_PASSWORD,
            db=self.config.REDIS_DB,
            decode_responses=True
        )

    async def get_recommendations(self, user_id: int):
        """Cache user recommendations"""
        if not self.redis:
            return None
        key = f"reco:user:{user_id}"
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None

    async def set_recommendations(self, user_id: int, recommendations: list, expire: int = 300):
        """Cache user recommendations for 5 minutes"""
        if not self.redis:
            return
        key = f"reco:user:{user_id}"
        await self.redis.setex(key, expire, json.dumps(recommendations))

    async def get_popular_items(self, community: str):
        """Cache popular items by community"""
        key = f"popular:{community}"
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None

    async def set_popular_items(self, community: str, items: list, expire: int = 3600):
        """Cache popular items for 1 hour"""
        key = f"popular:{community}"
        await self.redis.setex(key, expire, json.dumps(items))

# Singleton instance
cache_service = CacheService(CacheConfig())

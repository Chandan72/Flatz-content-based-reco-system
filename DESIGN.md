# FlatZ Recommendation System - Design Note

## Architecture Overview
- Multi-layered recommendation system
- Hybrid approach combining content, collaborative, and popularity signals
- Policy & safety enforcement layer

## Privacy & Safety Considerations
- Community isolation to protect user privacy
- Content quality filtering
- Creator frequency caps to prevent spam
- User interaction logging with consent

## Scalability Design
- Stateless FastAPI architecture for horizontal scaling
- In-memory caching for embeddings and popularity
- Database connection pooling
- Future: Redis caching, read replicas, async processing

## ML Model Choices
- Content-based: sentence-transformers + FAISS for semantic similarity
- Collaborative: Item-item similarity using cosine distance
- Popularity: Time-decayed scoring with community isolation
- Ranking: Weighted feature combination (extensible to LTR models)

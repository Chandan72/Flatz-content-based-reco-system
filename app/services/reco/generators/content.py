# app/services/reco/generators/content.py

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.core.models import Item

class ContentGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load a small, fast sentence-transformer
        self.model = SentenceTransformer(model_name)
        self.index = None         # FAISS index
        self.item_ids = []        # Mapping from FAISS idx → item.id

    def build_index(self, db: Session):
        # 1. Fetch all items
        items = db.query(Item).all()
        texts = []
        self.item_ids = []
        for item in items:
            # Combine title + description + community
            text = f"{item.title}. {item.description} [{item.community}]"
            texts.append(text)
            self.item_ids.append(item.id)

        # 2. Compute embeddings
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        dim = embeddings.shape[1]

        # 3. Build and populate FAISS L2 index
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

    def get_similar(self, text: str, top_k: int = 10) -> list[int]:
        if self.index is None:
            raise RuntimeError("Index not built")
        # Encode the query
        q_emb = self.model.encode([text], convert_to_numpy=True)
        # Search for top_k nearest neighbors
        distances, indices = self.index.search(q_emb, top_k)
        # Map FAISS indices back to item IDs
        return [ self.item_ids[i] for i in indices[0]]
content_gen= ContentGenerator()


from fastapi import FastAPI
from app.api.v1.routers.reco import router as reco_router
from app.core.db import SessionLocal
from app.services.reco.generators.content import content_gen  # now imported from content.py
import logging
from app.services.reco.generators.popularity import pop_gen
from app.api.v1.routers.feedback import router as feedback_router
from app.services.reco.generators.collaborative import cf_generator
from app.services.cache_service import cache_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="FlatZ Reco Service")

@app.on_event("startup")
def on_startup():
    
    """
    Runs once when the server starts.
    Builds the content-based recommendation index from existing items in DB.
    """
    with SessionLocal() as db:  # context manager ensures closure
        logger.info("🚀 Building content-based FAISS index...")
        content_gen.build_index(db)
        
        logger.info("✅ Index built successfully with %d items", len(content_gen.item_ids))
        pop_gen.refresh(db)
        logger.info("✅ popularity ranking built successfully")
        logger.info("Building collaborative filtering model...")
        cf_generator.build_model(db)
        logger.info("✅ CF model successfully")

@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "ok"}

# Include  recommendation routes
app.include_router(reco_router, prefix="/v1/reco",tags=["reco"])
# Include the feedback routes
app.include_router(feedback_router, prefix="/v1/reco", tags=["feedback"])

@app.get("/")
async def root():
    """Default landing endpoint."""
    return {"message": "Welcome to FlatZ Reco Service"}


from fastapi import FastAPI
from app.api.v1.routers.reco import router as reco_router

app = FastAPI(title="FlatZ Reco Service")

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(reco_router, prefix="/v1/reco", tags=["reco"])
@app.get("/")
async def root():
    return {"message": "Welcome to FlatZ Reco Service"}


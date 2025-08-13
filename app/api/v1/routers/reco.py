from fastapi import APIRouter, Query
from app.api.v1.schemas.reco import HomefeedResponse

router = APIRouter()

@router.get("/homefeed", response_model=HomefeedResponse)
async def homefeed(user_id: int = Query(..., description="User ID")):
    # TODO: replace [] with real recommendations later
    return {"user_id": user_id, "recommendations": []}

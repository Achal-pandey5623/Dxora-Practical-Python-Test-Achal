from fastapi import FastAPI

from app.config import get_settings
from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import publish

app = FastAPI(title="Automated Multi-Platform Posting System", version="1.0.0")


@app.post("/posting", response_model=PostingResponse)
async def create_posts(payload: PostingRequest) -> PostingResponse:
    results = await publish(payload.message, get_settings())
    return PostingResponse(success=any(result.status == "success" for result in results), results=results)


@app.get("/health")
async def health():
    return {"status": "ok"}

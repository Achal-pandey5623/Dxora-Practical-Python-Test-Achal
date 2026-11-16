from fastapi import FastAPI

from app.config import get_settings
from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import publish

app = FastAPI(title="Automated Multi-Platform Posting System", version="1.0.0")


@app.post("/posting", response_model=PostingResponse)
async def create_posts(payload: PostingRequest) -> PostingResponse:
    settings = get_settings()
    results = await publish(payload.message, settings, dry_run=settings.dry_run)
    succeeded = (all(result.status == "dry_run" for result in results) if settings.dry_run
                 else any(result.status == "success" for result in results))
    return PostingResponse(success=succeeded, mode="dry_run" if settings.dry_run else "live", results=results)


@app.get("/health")
async def health():
    return {"status": "ok"}

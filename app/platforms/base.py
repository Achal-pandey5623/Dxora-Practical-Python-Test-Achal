from abc import ABC, abstractmethod
from datetime import datetime, timezone

import httpx

from app.config import Settings
from app.schemas import PlatformResult


class PostingPlatform(ABC):
    name: str

    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    async def post(self, message: str) -> PlatformResult:
        raise NotImplementedError

    def failed(self, reason: str) -> PlatformResult:
        return PlatformResult(platform=self.name, status="failed", public_access=False, error=reason[:500])

    def succeeded(self, url: str | None, *, public: bool = True) -> PlatformResult:
        now = datetime.now(timezone.utc)
        return PlatformResult(platform=self.name, status="success", posted_url=url,
                              public_access=public, date=now.date(), time=now.time().replace(tzinfo=None))

    async def request_error(self, exc: Exception) -> PlatformResult:
        if isinstance(exc, httpx.HTTPStatusError):
            response = exc.response
            detail = response.text[:300] or response.reason_phrase
            return self.failed(f"HTTP {response.status_code}: {detail}")
        if isinstance(exc, httpx.TimeoutException):
            return self.failed("Request timed out")
        if isinstance(exc, httpx.RequestError):
            return self.failed(f"Network error: {exc}")
        return self.failed(str(exc) or exc.__class__.__name__)

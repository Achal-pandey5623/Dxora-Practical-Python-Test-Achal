from datetime import date as Date, time as Time
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class PostingRequest(BaseModel):
    message: str = Field(min_length=1, max_length=200)

    @field_validator("message")
    @classmethod
    def non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message cannot be blank")
        return value

    @model_validator(mode="after")
    def exactly_one_http_link(self):
        import re

        urls = re.findall(r"https?://[^\s<>\"']+", self.message)
        if len(urls) != 1:
            raise ValueError("message must contain exactly one CTA link")
        candidate = urls[0].rstrip(".,;:!?) ]}")
        try:
            HttpUrl(candidate)
        except Exception as exc:
            raise ValueError("CTA link must be a valid HTTP or HTTPS URL") from exc
        return self


class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed", "dry_run"]
    posted_url: str | None = None
    public_access: bool
    date: Date | None = None
    time: Time | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool
    mode: Literal["dry_run", "live"]
    results: list[PlatformResult]

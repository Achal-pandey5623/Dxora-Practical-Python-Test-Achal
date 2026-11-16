from urllib.parse import urlparse

import httpx

from app.platforms.base import PostingPlatform


class MastodonPlatform(PostingPlatform):
    name = "Mastodon"

    async def post(self, message: str):
        if not self.settings.mastodon_instance_url or not self.settings.mastodon_access_token:
            return self.failed("Not configured: set MASTODON_INSTANCE_URL and MASTODON_ACCESS_TOKEN")
        base = self.settings.mastodon_instance_url.rstrip("/")
        if urlparse(base).scheme != "https":
            return self.failed("MASTODON_INSTANCE_URL must use HTTPS")
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.post(f"{base}/api/v1/statuses",
                    headers={"Authorization": f"Bearer {self.settings.mastodon_access_token}"},
                    data={"status": message, "visibility": "public"})
                response.raise_for_status()
                body = response.json()
                return self.succeeded(body.get("url"), public=body.get("visibility") == "public")
        except Exception as exc:
            return await self.request_error(exc)

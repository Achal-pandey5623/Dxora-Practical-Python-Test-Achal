import httpx

from app.platforms.base import PostingPlatform


class XPlatform(PostingPlatform):
    name = "X"

    async def post(self, message: str):
        if not self.settings.x_user_access_token:
            return self.failed("Not configured: set X_USER_ACCESS_TOKEN with write access")
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.post("https://api.x.com/2/tweets",
                    headers={"Authorization": f"Bearer {self.settings.x_user_access_token}"},
                    json={"text": message})
                response.raise_for_status()
                post_id = response.json().get("data", {}).get("id")
                return self.succeeded(f"https://x.com/i/status/{post_id}" if post_id else None)
        except Exception as exc:
            return await self.request_error(exc)

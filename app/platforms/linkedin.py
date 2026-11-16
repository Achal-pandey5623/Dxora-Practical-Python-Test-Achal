import httpx

from app.platforms.base import PostingPlatform


class LinkedInPlatform(PostingPlatform):
    name = "LinkedIn"

    async def post(self, message: str):
        s = self.settings
        if not s.linkedin_access_token or not s.linkedin_author_urn:
            return self.failed("Not configured: set LINKEDIN_ACCESS_TOKEN and LINKEDIN_AUTHOR_URN")
        try:
            async with httpx.AsyncClient(timeout=s.request_timeout_seconds) as client:
                response = await client.post("https://api.linkedin.com/rest/posts",
                    headers={"Authorization": f"Bearer {s.linkedin_access_token}",
                             "Linkedin-Version": s.linkedin_api_version,
                             "X-Restli-Protocol-Version": "2.0.0",
                             "Content-Type": "application/json"},
                    json={"author": s.linkedin_author_urn, "commentary": message,
                          "visibility": "PUBLIC",
                          "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [],
                                           "thirdPartyDistributionChannels": []},
                          "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False})
                response.raise_for_status()
                post_id = response.headers.get("x-restli-id")
                url = f"https://www.linkedin.com/feed/update/{post_id}" if post_id else None
                return self.succeeded(url)
        except Exception as exc:
            return await self.request_error(exc)

import httpx

from app.platforms.base import PostingPlatform


class RedditPlatform(PostingPlatform):
    name = "Reddit"

    async def post(self, message: str):
        s = self.settings
        needed = [s.reddit_client_id, s.reddit_client_secret, s.reddit_username,
                  s.reddit_password, s.reddit_subreddit]
        if not all(needed):
            return self.failed("Not configured: set Reddit client credentials, username, password, and subreddit")
        try:
            async with httpx.AsyncClient(timeout=s.request_timeout_seconds) as client:
                token_response = await client.post("https://www.reddit.com/api/v1/access_token",
                    auth=(s.reddit_client_id, s.reddit_client_secret),
                    data={"grant_type": "password", "username": s.reddit_username,
                          "password": s.reddit_password},
                    headers={"User-Agent": s.reddit_user_agent})
                token_response.raise_for_status()
                token = token_response.json()["access_token"]
                submit = await client.post("https://oauth.reddit.com/api/submit",
                    headers={"Authorization": f"Bearer {token}", "User-Agent": s.reddit_user_agent},
                    data={"api_type": "json", "kind": "self", "sr": s.reddit_subreddit,
                          "title": s.reddit_title, "text": message, "resubmit": "true"})
                submit.raise_for_status()
                body = submit.json()
                errors = body.get("json", {}).get("errors", [])
                if errors:
                    return self.failed("Reddit rejected submission: " + "; ".join(map(str, errors)))
                data = body.get("json", {}).get("data", {})
                permalink = data.get("url") or data.get("permalink")
                if permalink and permalink.startswith("/"):
                    permalink = f"https://www.reddit.com{permalink}"
                return self.succeeded(permalink)
        except Exception as exc:
            return await self.request_error(exc)

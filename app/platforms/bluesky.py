from datetime import datetime, timezone
import re

import httpx

from app.platforms.base import PostingPlatform


class BlueskyPlatform(PostingPlatform):
    name = "Bluesky"

    async def post(self, message: str):
        if not self.settings.bluesky_handle or not self.settings.bluesky_app_password:
            return self.failed("Not configured: set BLUESKY_HANDLE and BLUESKY_APP_PASSWORD")
        base = self.settings.bluesky_pds_url.rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                login = await client.post(f"{base}/xrpc/com.atproto.server.createSession",
                    json={"identifier": self.settings.bluesky_handle,
                          "password": self.settings.bluesky_app_password})
                login.raise_for_status()
                session = login.json()
                now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                facets = []
                for match in re.finditer(r"https?://[^\s<>\"']+", message):
                    link = match.group(0).rstrip(".,;:!?) ]}")
                    start = len(message[:match.start()].encode("utf-8"))
                    end = start + len(link.encode("utf-8"))
                    facets.append({"index": {"byteStart": start, "byteEnd": end},
                                   "features": [{"$type": "app.bsky.richtext.facet#link", "uri": link}]})
                post = await client.post(f"{base}/xrpc/com.atproto.repo.createRecord",
                    headers={"Authorization": f"Bearer {session['accessJwt']}"},
                    json={"repo": session["did"], "collection": "app.bsky.feed.post",
                          "record": {"$type": "app.bsky.feed.post", "text": message,
                                     "createdAt": now, "facets": facets}})
                post.raise_for_status()
                body = post.json()
                rkey = body["uri"].rsplit("/", 1)[-1]
                handle = session.get("handle", self.settings.bluesky_handle)
                return self.succeeded(f"https://bsky.app/profile/{handle}/post/{rkey}")
        except Exception as exc:
            return await self.request_error(exc)

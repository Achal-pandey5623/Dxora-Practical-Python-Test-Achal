import asyncio

from app.config import Settings
from app.platforms import BlueskyPlatform, LinkedInPlatform, MastodonPlatform, RedditPlatform, XPlatform
from app.schemas import PlatformResult


async def publish(message: str, settings: Settings, *, dry_run: bool = False) -> list[PlatformResult]:
    platforms = [MastodonPlatform(settings), BlueskyPlatform(settings), RedditPlatform(settings),
                 LinkedInPlatform(settings), XPlatform(settings)]
    if dry_run:
        # Return simulated results without calling any platform or making network requests.
        return [PlatformResult(platform=platform.name, status="dry_run", public_access=False)
                for platform in platforms]
    # Each platform catches its own failures; gather keeps all other posts running.
    return await asyncio.gather(*(platform.post(message) for platform in platforms))

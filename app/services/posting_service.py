import asyncio

from app.config import Settings
from app.platforms import BlueskyPlatform, LinkedInPlatform, MastodonPlatform, RedditPlatform, XPlatform
from app.schemas import PlatformResult


async def publish(message: str, settings: Settings) -> list[PlatformResult]:
    platforms = [MastodonPlatform(settings), BlueskyPlatform(settings), RedditPlatform(settings),
                 LinkedInPlatform(settings), XPlatform(settings)]
    # Each platform catches its own failures; gather keeps all other posts running.
    return await asyncio.gather(*(platform.post(message) for platform in platforms))

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    request_timeout_seconds: float = 20.0

    mastodon_instance_url: str | None = None
    mastodon_access_token: str | None = None

    bluesky_handle: str | None = None
    bluesky_app_password: str | None = None
    bluesky_pds_url: str = "https://bsky.social"

    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_username: str | None = None
    reddit_password: str | None = None
    reddit_subreddit: str | None = None
    reddit_title: str = "An update"
    reddit_user_agent: str = "automated-multi-platform-posting/1.0"

    linkedin_access_token: str | None = None
    linkedin_author_urn: str | None = None
    linkedin_api_version: str = "202610"

    x_user_access_token: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()

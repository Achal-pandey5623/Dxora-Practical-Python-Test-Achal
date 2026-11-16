# Automated Multi-Platform Posting System

A FastAPI service that accepts a short message with exactly one HTTP(S) link and independently attempts to publish it to Mastodon, Bluesky, Reddit, LinkedIn, and X. Missing credentials and platform API errors are reported per platform; one failure does not prevent the other attempts.

## Requirements and setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
Copy-Item .env.example .env  # PowerShell; edit .env with your credentials
```

Run the API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Interactive API docs: <http://localhost:4000/docs>. Health check: `GET /health`.

## Request

```http
POST http://localhost:4000/posting
Content-Type: application/json
```

```json
{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

Messages must be 1–200 characters and contain exactly one valid HTTP(S) link. Platform selection is internal. A request returns one result per platform, including unconfigured platforms.

## Response

```json
{
  "success": true,
  "results": [
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://mastodon.social/@account/123456",
      "public_access": true,
      "date": "2026-11-16",
      "time": "10:30:00",
      "error": null
    },
    {
      "platform": "X",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Not configured: set X_USER_ACCESS_TOKEN with write access"
    }
  ]
}
```

The success value is true when at least one platform publishes successfully. Timestamps are UTC. `public_access` is set true after successful publication where this implementation requests public visibility. The API cannot independently guarantee visibility to a logged-out visitor if a platform or account applies restrictions.

## Platform setup

All credentials are optional. Configure only platforms for which you have developer access. Obtain credentials from each platform and set them in `.env`:

| Platform | Environment settings | Requirements |
|---|---|---|
| Mastodon | `MASTODON_INSTANCE_URL`, `MASTODON_ACCESS_TOKEN` | User token with `write:statuses`; this app explicitly requests public visibility. |
| Bluesky | `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`, `BLUESKY_PDS_URL` | Use an app password. Service creates a session and an `app.bsky.feed.post` record. |
| Reddit | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`, `REDDIT_SUBREDDIT` | Reddit OAuth app; the account must be allowed to submit to the configured subreddit. `REDDIT_TITLE` supplies the required title; message is submitted as the body. |
| LinkedIn | `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN`, `LINKEDIN_API_VERSION` | Approved Community Management access and `w_member_social`, or organization posting permission and a `urn:li:organization:...` author URN. API access is not generally granted to every app. |
| X | `X_USER_ACCESS_TOKEN` | OAuth 2.0 user-context token with `tweet.write` (and `users.read`) and an API access tier that permits posting. An app-only bearer token is not sufficient. |

Never commit `.env` or tokens. `.env.example` contains placeholders only. Tokens may expire or need reauthorization. Use test accounts and ensure that you have permission to publish to each destination.

## Integration references

- [Mastodon: Create a status](https://docs.joinmastodon.org/methods/statuses/)
- [Bluesky: Creating a post](https://docs.bsky.app/docs/tutorials/creating-a-post)
- [Bluesky: `com.atproto.repo.createRecord`](https://docs.bsky.app/docs/api/com-atproto-repo-create-record)
- [Reddit Developer Platform](https://developers.reddit.com/docs)
- [LinkedIn: Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [X API: Manage Posts](https://developer.x.com/en/docs/x-api/tweets/manage-tweets/api-reference/post-tweets)

## Design notes

- FastAPI/Pydantic validate the request before any network calls.
- Integrations use async HTTPX and configurable request timeouts.
- Platforms run concurrently. Each adapter catches and returns its own error, so partial success is represented in the response.
- In an actual deployment, protect this endpoint with authentication and rate limits. It can publish externally as soon as valid credentials are configured.

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("app.main.get_settings", lambda: Settings(dry_run=True))
    return TestClient(app)


def test_posting_dry_run_returns_one_simulated_result_per_platform(client, monkeypatch):
    def unexpected_network_call(*args, **kwargs):
        pytest.fail("Dry-run must not create an HTTP client or call a platform")

    monkeypatch.setattr("httpx.AsyncClient", unexpected_network_call)

    response = client.post(
        "/posting",
        json={"message": "Local test only. https://example.com"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["mode"] == "dry_run"
    assert {result["platform"] for result in body["results"]} == {
        "Mastodon", "Bluesky", "Reddit", "LinkedIn", "X"
    }
    for result in body["results"]:
        assert result["status"] == "dry_run"
        assert result["posted_url"] is None
        assert result["public_access"] is False
        assert result["date"] is None
        assert result["time"] is None
        assert result["error"] is None


@pytest.mark.parametrize(
    "message",
    [
        "A message without a link",
        "Two links: https://example.com and https://example.org",
        "x" * 190 + " https://example.com",
    ],
)
def test_posting_rejects_invalid_message(client, message):
    response = client.post("/posting", json={"message": message})

    assert response.status_code == 422

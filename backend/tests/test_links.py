from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient


def test_posting_same_url_twice_returns_same_slug(client: TestClient) -> None:
    body = {"url": "https://example.com/page"}

    first = client.post("/links", json=body)
    second = client.post("/links", json=body)

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["slug"] == first.json()["slug"]


def test_simultaneous_clicks_are_all_counted(client: TestClient) -> None:
    created = client.post("/links", json={"url": "https://example.com/page"})
    slug = created.json()["slug"]
    CLICKS = 50

    def click(_: int) -> int:
        return int(client.get(f"/{slug}", follow_redirects=False).status_code)

    with ThreadPoolExecutor(max_workers=CLICKS) as pool:
        statuses = list(pool.map(click, range(CLICKS)))

    stats = client.get(f"/links/{slug}/stats")

    assert statuses == [302] * CLICKS
    assert stats.json()["clicks"] == CLICKS

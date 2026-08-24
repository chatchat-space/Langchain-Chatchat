import pytest

from chatchat.server.search_engine.xquik import xquik_search


class SearchResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.raise_calls = 0

    def json(self):
        return self.payload

    def raise_for_status(self):
        self.raise_calls += 1


def test_xquik_search_maps_posts_and_protects_credentials():
    calls = []
    response = SearchResponse(
        {
            "tweets": [
                {
                    "id": "123",
                    "text": "  First result  ",
                    "author": {"username": "example_user"},
                },
                {"id": "456", "text": "Second result"},
                "invalid row",
                {"text": "No ID result"},
                {"id": "789", "text": "   "},
            ]
        }
    )

    def request_get(url, **kwargs):
        calls.append((url, kwargs))
        return response

    results = xquik_search(
        "agent news",
        {"query_type": "Top", "timeout": 500},
        500,
        request_get=request_get,
        environ={"X_TWITTER_SCRAPER_API_KEY": "secret-key"},
    )

    assert results == [
        {
            "snippet": "First result",
            "link": "https://x.com/example_user/status/123",
            "title": "@example_user on X",
        },
        {
            "snippet": "Second result",
            "link": "https://x.com/i/status/456",
            "title": "X post 456",
        },
        {
            "snippet": "No ID result",
            "link": "https://x.com",
            "title": "X post",
        },
    ]
    assert calls == [
        (
            "https://xquik.com/api/v1/x/tweets/search",
            {
                "params": {"q": "agent news", "limit": 100, "queryType": "Top"},
                "headers": {"x-api-key": "secret-key"},
                "timeout": 120,
                "allow_redirects": False,
            },
        )
    ]
    assert response.raise_calls == 1


def test_xquik_search_applies_minimum_bounds():
    calls = []

    def request_get(url, **kwargs):
        calls.append((url, kwargs))
        return SearchResponse({"tweets": []})

    assert (
        xquik_search(
            "agent news",
            {"timeout": 0},
            0,
            request_get=request_get,
            environ={"X_TWITTER_SCRAPER_API_KEY": "secret-key"},
        )
        == []
    )
    assert calls[0][1]["params"] == {
        "q": "agent news",
        "limit": 1,
        "queryType": "Latest",
    }
    assert calls[0][1]["timeout"] == 1


def test_xquik_search_requires_an_environment_key():
    with pytest.raises(
        ValueError, match="X_TWITTER_SCRAPER_API_KEY is required for Xquik search"
    ):
        xquik_search("agent news", {}, 5, environ={})


@pytest.mark.parametrize("query_type", ["latest", "Recent", ""])
def test_xquik_search_rejects_unknown_query_types(query_type):
    with pytest.raises(ValueError, match="query_type must be Latest or Top"):
        xquik_search(
            "agent news",
            {"query_type": query_type},
            5,
            environ={"X_TWITTER_SCRAPER_API_KEY": "secret-key"},
        )


def test_xquik_search_rejects_redirects():
    response = SearchResponse({}, status_code=302)

    with pytest.raises(ValueError, match="refused an HTTP redirect"):
        xquik_search(
            "agent news",
            {},
            5,
            request_get=lambda *args, **kwargs: response,
            environ={"X_TWITTER_SCRAPER_API_KEY": "secret-key"},
        )

    assert response.raise_calls == 0


@pytest.mark.parametrize("payload", [None, [], {}, {"tweets": None}])
def test_xquik_search_rejects_invalid_responses(payload):
    with pytest.raises(ValueError, match="returned an invalid response"):
        xquik_search(
            "agent news",
            {},
            5,
            request_get=lambda *args, **kwargs: SearchResponse(payload),
            environ={"X_TWITTER_SCRAPER_API_KEY": "secret-key"},
        )

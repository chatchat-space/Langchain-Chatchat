from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Mapping
from urllib.parse import quote

import requests

XQUIK_MAX_RESULTS = 100
XQUIK_SEARCH_URL = "https://xquik.com/api/v1/x/tweets/search"
XQUIK_TIMEOUT_SECONDS = 30


def _result_url(tweet: Mapping[str, Any]) -> str:
    tweet_id = str(tweet.get("id") or "").strip()
    if not tweet_id:
        return "https://x.com"

    author = tweet.get("author")
    username = author.get("username") if isinstance(author, dict) else None
    username = str(username or "").lstrip("@").strip()
    if username:
        safe_username = quote(username, safe="")
        safe_tweet_id = quote(tweet_id, safe="")
        return f"https://x.com/{safe_username}/status/{safe_tweet_id}"
    return f"https://x.com/i/status/{quote(tweet_id, safe='')}"


def _result_title(tweet: Mapping[str, Any]) -> str:
    author = tweet.get("author")
    username = author.get("username") if isinstance(author, dict) else None
    username = str(username or "").lstrip("@").strip()
    if username:
        return f"@{username} on X"

    tweet_id = str(tweet.get("id") or "").strip()
    return f"X post {tweet_id}" if tweet_id else "X post"


def xquik_search(
    text: str,
    config: Dict[str, Any],
    top_k: int,
    *,
    request_get: Callable[..., Any] = requests.get,
    environ: Mapping[str, str] = os.environ,
) -> List[Dict[str, str]]:
    """Search X posts through Xquik and return Chatchat search results."""
    api_key = environ.get("X_TWITTER_SCRAPER_API_KEY", "").strip()
    if not api_key:
        raise ValueError("X_TWITTER_SCRAPER_API_KEY is required for Xquik search")

    query_type = str(config.get("query_type", "Latest"))
    if query_type not in {"Latest", "Top"}:
        raise ValueError("Xquik query_type must be Latest or Top")

    timeout = max(1, min(int(config.get("timeout", XQUIK_TIMEOUT_SECONDS)), 120))
    limit = max(1, min(int(top_k), XQUIK_MAX_RESULTS))
    response = request_get(
        XQUIK_SEARCH_URL,
        params={"q": text, "limit": limit, "queryType": query_type},
        headers={"x-api-key": api_key},
        timeout=timeout,
        allow_redirects=False,
    )
    if 300 <= response.status_code < 400:
        raise ValueError("Xquik search refused an HTTP redirect")
    response.raise_for_status()

    payload = response.json()
    tweets = payload.get("tweets") if isinstance(payload, dict) else None
    if not isinstance(tweets, list):
        raise ValueError("Xquik search returned an invalid response")

    results = []
    for tweet in tweets:
        if not isinstance(tweet, dict):
            continue
        text = str(tweet.get("text") or "").strip()
        if not text:
            continue
        results.append(
            {
                "snippet": text,
                "link": _result_url(tweet),
                "title": _result_title(tweet),
            }
        )
    return results

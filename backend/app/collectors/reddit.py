from __future__ import annotations
import logging
from typing import Any
from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

REDDIT_BASE = "https://www.reddit.com/r"


class RedditCollector(BaseCollector):
    BASE_URL = REDDIT_BASE

    def __init__(self) -> None:
        super().__init__(rate_limit=1.0, cache_ttl=1800)

    async def fetch(self) -> Any:
        return await self.fetch_subreddit_stats("bitcoin")

    async def fetch_subreddit_stats(self, subreddit: str) -> dict:
        cache_key = f"reddit_{subreddit}"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    f"{self.BASE_URL}/{subreddit}/about.json",
                    headers={"User-Agent": "CryptoTrend/1.0 (trend analysis bot)"},
                )
                if data and "data" in data:
                    d = data["data"]
                    return {
                        "subreddit": subreddit,
                        "subscribers": d.get("subscribers", 0),
                        "active_users": d.get("active_user_count", 0),
                        "description": d.get("public_description", ""),
                    }
                return _fallback_subreddit(subreddit)
            except Exception as exc:
                logger.warning("Reddit fetch_subreddit_stats failed for %s: %s", subreddit, exc)
                return _fallback_subreddit(subreddit)

        return await self.fetch_cached(cache_key, _fetch, ttl=1800) or _fallback_subreddit(subreddit)


def _fallback_subreddit(subreddit: str) -> dict:
    defaults = {
        "bitcoin": {"subscribers": 5_500_000, "active_users": 8000},
        "ethereum": {"subscribers": 1_700_000, "active_users": 3000},
        "cryptocurrency": {"subscribers": 6_800_000, "active_users": 10000},
    }
    d = defaults.get(subreddit, {"subscribers": 500_000, "active_users": 1000})
    return {"subreddit": subreddit, **d, "description": ""}

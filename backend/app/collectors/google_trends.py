from __future__ import annotations
import asyncio
import logging
from typing import Any
from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)


class GoogleTrendsCollector(BaseCollector):
    """Wrapper around pytrends (synchronous library run in executor)."""

    def __init__(self) -> None:
        super().__init__(rate_limit=0.1, cache_ttl=3600)

    async def fetch(self) -> Any:
        return await self.fetch_trends("bitcoin")

    async def fetch_trends(self, keyword: str, timeframe: str = "today 3-m") -> dict:
        cache_key = f"gtrends_{keyword}_{timeframe.replace(' ', '_')}"

        async def _fetch():
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, _sync_fetch_trends, keyword, timeframe)
                return result
            except Exception as exc:
                logger.warning("Google Trends fetch failed for '%s': %s", keyword, exc)
                return _fallback_trends(keyword)

        return await self.fetch_cached(cache_key, _fetch, ttl=3600) or _fallback_trends(keyword)


def _sync_fetch_trends(keyword: str, timeframe: str) -> dict:
    from pytrends.request import TrendReq  # type: ignore

    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
    pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo="", gprop="")
    df = pytrends.interest_over_time()
    if df is None or df.empty:
        return _fallback_trends(keyword)
    values = df[keyword].tolist() if keyword in df.columns else []
    return {
        "keyword": keyword,
        "values": values,
        "latest": int(values[-1]) if values else 50,
        "avg": int(sum(values) / len(values)) if values else 50,
        "max": int(max(values)) if values else 100,
    }


def _fallback_trends(keyword: str) -> dict:
    return {"keyword": keyword, "values": [50] * 30, "latest": 50, "avg": 50, "max": 100}

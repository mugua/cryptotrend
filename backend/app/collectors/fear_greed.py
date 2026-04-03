from __future__ import annotations
import logging
from typing import Any
from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

FEAR_GREED_BASE = "https://api.alternative.me/fng/"

_CLASSIFICATIONS = {
    (0, 24): "Extreme Fear",
    (25, 44): "Fear",
    (45, 55): "Neutral",
    (56, 74): "Greed",
    (75, 100): "Extreme Greed",
}


def _classify(value: int) -> str:
    for (low, high), label in _CLASSIFICATIONS.items():
        if low <= value <= high:
            return label
    return "Neutral"


class FearGreedCollector(BaseCollector):
    BASE_URL = FEAR_GREED_BASE

    def __init__(self) -> None:
        super().__init__(rate_limit=0.5, cache_ttl=1800)

    async def fetch(self) -> Any:
        return await self.fetch_current()

    async def fetch_current(self) -> dict:
        cache_key = "fg_current"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    self.BASE_URL,
                    params={"limit": 1, "format": "json"},
                )
                if data and "data" in data and data["data"]:
                    entry = data["data"][0]
                    value = int(entry.get("value", 50))
                    return {
                        "value": value,
                        "classification": entry.get("value_classification", _classify(value)),
                        "timestamp": entry.get("timestamp", ""),
                    }
                return _fallback_current()
            except Exception as exc:
                logger.warning("FearGreed fetch_current failed: %s", exc)
                return _fallback_current()

        return await self.fetch_cached(cache_key, _fetch, ttl=1800) or _fallback_current()

    async def fetch_history(self, limit: int = 30) -> list[dict]:
        cache_key = f"fg_history_{limit}"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    self.BASE_URL,
                    params={"limit": limit, "format": "json"},
                )
                if data and "data" in data:
                    result = []
                    for entry in data["data"]:
                        value = int(entry.get("value", 50))
                        result.append({
                            "value": value,
                            "classification": entry.get("value_classification", _classify(value)),
                            "timestamp": entry.get("timestamp", ""),
                        })
                    return result
                return _fallback_history(limit)
            except Exception as exc:
                logger.warning("FearGreed fetch_history failed: %s", exc)
                return _fallback_history(limit)

        return await self.fetch_cached(cache_key, _fetch, ttl=3600) or _fallback_history(limit)


def _fallback_current() -> dict:
    return {"value": 50, "classification": "Neutral", "timestamp": ""}


def _fallback_history(limit: int) -> list[dict]:
    return [{"value": 50, "classification": "Neutral", "timestamp": ""} for _ in range(limit)]

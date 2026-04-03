from __future__ import annotations
import logging
from typing import Any, Optional
from app.collectors.base import BaseCollector
from app.config import get_settings

logger = logging.getLogger(__name__)

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    "dxy": "DTWEXBGS",
    "treasury_10y": "DGS10",
    "vix": "VIXCLS",
    "m2": "M2SL",
}


class FREDCollector(BaseCollector):
    BASE_URL = FRED_BASE

    def __init__(self) -> None:
        settings = get_settings()
        super().__init__(rate_limit=0.5, cache_ttl=21600)
        self._api_key = settings.fred_api_key

    async def fetch(self) -> Any:
        return await self.fetch_dxy()

    async def _fetch_series(self, series_id: str, limit: int = 30) -> list[dict]:
        if not self._api_key:
            logger.debug("FRED API key not set; using fallback for %s", series_id)
            return []
        try:
            data = await self._get_with_retry(
                self.BASE_URL,
                params={
                    "series_id": series_id,
                    "api_key": self._api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": limit,
                },
            )
            if data and "observations" in data:
                obs = []
                for o in data["observations"]:
                    try:
                        obs.append({"date": o["date"], "value": float(o["value"])})
                    except (ValueError, KeyError):
                        continue
                obs.reverse()
                return obs
        except Exception as exc:
            logger.warning("FRED series %s failed: %s", series_id, exc)
        return []

    async def fetch_dxy(self) -> dict:
        cache_key = "fred_dxy"

        async def _fetch():
            obs = await self._fetch_series(SERIES["dxy"])
            if obs:
                values = [o["value"] for o in obs]
                return {"values": values, "latest": values[-1], "avg_30d": sum(values) / len(values)}
            return {"values": [104.0] * 20, "latest": 104.0, "avg_30d": 104.0}

        return await self.fetch_cached(cache_key, _fetch, ttl=21600) or {"values": [104.0] * 20, "latest": 104.0, "avg_30d": 104.0}

    async def fetch_treasury_yield(self) -> dict:
        cache_key = "fred_treasury_10y"

        async def _fetch():
            obs = await self._fetch_series(SERIES["treasury_10y"])
            if obs:
                values = [o["value"] for o in obs]
                return {"values": values, "latest": values[-1], "avg_30d": sum(values) / len(values)}
            return {"values": [4.5] * 20, "latest": 4.5, "avg_30d": 4.5}

        return await self.fetch_cached(cache_key, _fetch, ttl=21600) or {"values": [4.5] * 20, "latest": 4.5, "avg_30d": 4.5}

    async def fetch_vix(self) -> dict:
        cache_key = "fred_vix"

        async def _fetch():
            obs = await self._fetch_series(SERIES["vix"])
            if obs:
                values = [o["value"] for o in obs]
                return {"values": values, "latest": values[-1], "avg_30d": sum(values) / len(values)}
            return {"values": [18.0] * 20, "latest": 18.0, "avg_30d": 18.0}

        return await self.fetch_cached(cache_key, _fetch, ttl=21600) or {"values": [18.0] * 20, "latest": 18.0, "avg_30d": 18.0}

    async def fetch_m2(self) -> dict:
        cache_key = "fred_m2"

        async def _fetch():
            obs = await self._fetch_series(SERIES["m2"], limit=13)
            if obs:
                values = [o["value"] for o in obs]
                yoy_change = ((values[-1] - values[0]) / values[0] * 100) if len(values) > 1 else 0.0
                return {"values": values, "latest": values[-1], "yoy_change_pct": yoy_change}
            return {"values": [21000.0] * 13, "latest": 21000.0, "yoy_change_pct": 2.0}

        return await self.fetch_cached(cache_key, _fetch, ttl=86400) or {"values": [21000.0] * 13, "latest": 21000.0, "yoy_change_pct": 2.0}

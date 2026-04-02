from __future__ import annotations
import logging
from typing import Any, Optional
from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

BINANCE_BASE = "https://api.binance.com/api/v3"
BINANCE_FAPI = "https://fapi.binance.com/fapi/v1"


class BinanceCollector(BaseCollector):
    BASE_URL = BINANCE_BASE

    def __init__(self) -> None:
        super().__init__(rate_limit=5.0, cache_ttl=30)

    async def fetch(self) -> Any:
        return await self.fetch_klines("BTCUSDT")

    async def fetch_klines(
        self, symbol: str, interval: str = "1d", limit: int = 200
    ) -> dict:
        cache_key = f"bn_klines_{symbol}_{interval}_{limit}"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    f"{self.BASE_URL}/klines",
                    params={"symbol": symbol, "interval": interval, "limit": limit},
                )
                if not data:
                    return _empty_klines(symbol, interval)
                open_times, opens, highs, lows, closes, volumes = [], [], [], [], [], []
                for candle in data:
                    open_times.append(int(candle[0]))
                    opens.append(float(candle[1]))
                    highs.append(float(candle[2]))
                    lows.append(float(candle[3]))
                    closes.append(float(candle[4]))
                    volumes.append(float(candle[5]))
                return {
                    "symbol": symbol,
                    "interval": interval,
                    "open_time": open_times,
                    "open": opens,
                    "high": highs,
                    "low": lows,
                    "close": closes,
                    "volume": volumes,
                }
            except Exception as exc:
                logger.warning("Binance fetch_klines failed for %s: %s", symbol, exc)
                return _empty_klines(symbol, interval)

        return await self.fetch_cached(cache_key, _fetch, ttl=60) or _empty_klines(symbol, interval)

    async def fetch_funding_rate(self, symbol: str) -> dict:
        cache_key = f"bn_funding_{symbol}"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    f"{BINANCE_FAPI}/fundingRate",
                    params={"symbol": symbol, "limit": 1},
                )
                if data and isinstance(data, list) and data:
                    return {
                        "symbol": symbol,
                        "funding_rate": float(data[-1].get("fundingRate", 0)),
                        "funding_time": int(data[-1].get("fundingTime", 0)),
                    }
                return {"symbol": symbol, "funding_rate": 0.0001, "funding_time": 0}
            except Exception as exc:
                logger.warning("Binance fetch_funding_rate failed for %s: %s", symbol, exc)
                return {"symbol": symbol, "funding_rate": 0.0001, "funding_time": 0}

        return await self.fetch_cached(cache_key, _fetch, ttl=120) or {"symbol": symbol, "funding_rate": 0.0001, "funding_time": 0}

    async def fetch_open_interest(self, symbol: str) -> dict:
        cache_key = f"bn_oi_{symbol}"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    f"{BINANCE_FAPI}/openInterest",
                    params={"symbol": symbol},
                )
                if data:
                    return {
                        "symbol": symbol,
                        "open_interest": float(data.get("openInterest", 0)),
                        "time": int(data.get("time", 0)),
                    }
                return {"symbol": symbol, "open_interest": 0.0, "time": 0}
            except Exception as exc:
                logger.warning("Binance fetch_open_interest failed for %s: %s", symbol, exc)
                return {"symbol": symbol, "open_interest": 0.0, "time": 0}

        return await self.fetch_cached(cache_key, _fetch, ttl=120) or {"symbol": symbol, "open_interest": 0.0, "time": 0}

    async def fetch_long_short_ratio(self, symbol: str) -> dict:
        cache_key = f"bn_lsr_{symbol}"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    f"{BINANCE_FAPI}/globalLongShortAccountRatio",
                    params={"symbol": symbol, "period": "1d", "limit": 1},
                )
                if data and isinstance(data, list) and data:
                    entry = data[-1]
                    return {
                        "symbol": symbol,
                        "long_account": float(entry.get("longAccount", 0.5)),
                        "short_account": float(entry.get("shortAccount", 0.5)),
                        "long_short_ratio": float(entry.get("longShortRatio", 1.0)),
                    }
                return {"symbol": symbol, "long_account": 0.5, "short_account": 0.5, "long_short_ratio": 1.0}
            except Exception as exc:
                logger.warning("Binance fetch_long_short_ratio failed for %s: %s", symbol, exc)
                return {"symbol": symbol, "long_account": 0.5, "short_account": 0.5, "long_short_ratio": 1.0}

        return await self.fetch_cached(cache_key, _fetch, ttl=300) or {"symbol": symbol, "long_account": 0.5, "short_account": 0.5, "long_short_ratio": 1.0}


def _empty_klines(symbol: str, interval: str) -> dict:
    return {"symbol": symbol, "interval": interval, "open_time": [], "open": [], "high": [], "low": [], "close": [], "volume": []}

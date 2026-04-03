from __future__ import annotations
import logging
from datetime import datetime
from typing import Any, Optional
from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

DEFAULT_COINS = [
    "bitcoin",
    "ethereum",
    "binancecoin",
    "solana",
    "xrp",
    "cardano",
    "avalanche-2",
    "polkadot",
    "chainlink",
    "litecoin",
]

_FALLBACK_PRICES: dict[str, dict] = {
    "bitcoin": {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 45000, "price_change_percentage_24h": 0.5, "market_cap": 880000000000, "total_volume": 30000000000},
    "ethereum": {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 2400, "price_change_percentage_24h": 0.3, "market_cap": 290000000000, "total_volume": 15000000000},
}


class CoinGeckoCollector(BaseCollector):
    BASE_URL = COINGECKO_BASE

    def __init__(self) -> None:
        super().__init__(rate_limit=0.8, cache_ttl=60)

    async def fetch(self) -> Any:
        return await self.fetch_prices()

    async def fetch_prices(self, coins: list[str] = DEFAULT_COINS) -> list[dict]:
        cache_key = f"cg_prices_{'_'.join(sorted(coins))}"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    f"{self.BASE_URL}/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "ids": ",".join(coins),
                        "order": "market_cap_desc",
                        "per_page": len(coins),
                        "page": 1,
                        "sparkline": False,
                        "price_change_percentage": "24h",
                    },
                )
                return data or []
            except Exception as exc:
                logger.warning("CoinGecko fetch_prices failed: %s", exc)
                return [_FALLBACK_PRICES[c] for c in coins if c in _FALLBACK_PRICES]

        result = await self.fetch_cached(cache_key, _fetch, ttl=60)
        return result or []

    async def fetch_market_overview(self) -> dict:
        cache_key = "cg_market_overview"

        async def _fetch():
            try:
                data = await self._get_with_retry(f"{self.BASE_URL}/global")
                if not data:
                    return _fallback_overview()
                gd = data.get("data", {})
                mc = gd.get("market_cap_percentage", {})
                return {
                    "total_market_cap": gd.get("total_market_cap", {}).get("usd", 0),
                    "total_volume_24h": gd.get("total_volume", {}).get("usd", 0),
                    "btc_dominance": mc.get("btc", 0),
                    "eth_dominance": mc.get("eth", 0),
                    "stablecoin_market_cap": _estimate_stablecoin_cap(gd),
                    "active_coins": gd.get("active_cryptocurrencies", 0),
                    "last_updated": datetime.utcnow().isoformat(),
                }
            except Exception as exc:
                logger.warning("CoinGecko fetch_market_overview failed: %s", exc)
                return _fallback_overview()

        return await self.fetch_cached(cache_key, _fetch, ttl=120) or _fallback_overview()

    async def fetch_ohlcv(self, coin_id: str, days: int = 30) -> list[list]:
        cache_key = f"cg_ohlcv_{coin_id}_{days}"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    f"{self.BASE_URL}/coins/{coin_id}/ohlc",
                    params={"vs_currency": "usd", "days": days},
                )
                return data or []
            except Exception as exc:
                logger.warning("CoinGecko fetch_ohlcv failed for %s: %s", coin_id, exc)
                return []

        return await self.fetch_cached(cache_key, _fetch, ttl=300) or []


def _estimate_stablecoin_cap(global_data: dict) -> float:
    mc = global_data.get("market_cap_percentage", {})
    total_cap = global_data.get("total_market_cap", {}).get("usd", 1_000_000_000_000)
    stable_pct = sum(v for k, v in mc.items() if k in ("usdt", "usdc", "busd", "dai", "tusd", "usdp"))
    return total_cap * stable_pct / 100


def _fallback_overview() -> dict:
    return {
        "total_market_cap": 1_700_000_000_000,
        "total_volume_24h": 80_000_000_000,
        "btc_dominance": 52.0,
        "eth_dominance": 17.0,
        "stablecoin_market_cap": 140_000_000_000,
        "active_coins": 10000,
        "last_updated": datetime.utcnow().isoformat(),
    }

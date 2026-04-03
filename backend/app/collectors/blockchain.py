from __future__ import annotations
import logging
from typing import Any
from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

BLOCKCHAIN_BASE = "https://api.blockchain.info"


class BlockchainCollector(BaseCollector):
    BASE_URL = BLOCKCHAIN_BASE

    def __init__(self) -> None:
        super().__init__(rate_limit=0.5, cache_ttl=600)

    async def fetch(self) -> Any:
        return await self.fetch_active_addresses()

    async def fetch_active_addresses(self) -> dict:
        cache_key = "bc_active_addresses"

        async def _fetch():
            try:
                # n-unique-addresses chart (last 30 days)
                data = await self._get_with_retry(
                    f"{self.BASE_URL}/charts/n-unique-addresses",
                    params={"timespan": "30days", "format": "json", "sampled": "true"},
                )
                if data and "values" in data:
                    values = [v["y"] for v in data["values"] if "y" in v]
                    return {
                        "values": values,
                        "latest": values[-1] if values else 900000,
                        "avg_30d": sum(values) / len(values) if values else 900000,
                    }
                return _fallback_addresses()
            except Exception as exc:
                logger.warning("Blockchain fetch_active_addresses failed: %s", exc)
                return _fallback_addresses()

        return await self.fetch_cached(cache_key, _fetch, ttl=600) or _fallback_addresses()

    async def fetch_hash_rate(self) -> dict:
        cache_key = "bc_hash_rate"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    f"{self.BASE_URL}/charts/hash-rate",
                    params={"timespan": "30days", "format": "json", "sampled": "true"},
                )
                if data and "values" in data:
                    values = [v["y"] for v in data["values"] if "y" in v]
                    return {
                        "values": values,
                        "latest": values[-1] if values else 500e18,
                        "avg_30d": sum(values) / len(values) if values else 500e18,
                        "unit": "EH/s",
                    }
                return _fallback_hashrate()
            except Exception as exc:
                logger.warning("Blockchain fetch_hash_rate failed: %s", exc)
                return _fallback_hashrate()

        return await self.fetch_cached(cache_key, _fetch, ttl=3600) or _fallback_hashrate()

    async def fetch_transaction_volume(self) -> dict:
        cache_key = "bc_tx_volume"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    f"{self.BASE_URL}/charts/estimated-transaction-volume-usd",
                    params={"timespan": "30days", "format": "json", "sampled": "true"},
                )
                if data and "values" in data:
                    values = [v["y"] for v in data["values"] if "y" in v]
                    return {
                        "values": values,
                        "latest": values[-1] if values else 5_000_000_000,
                        "avg_30d": sum(values) / len(values) if values else 5_000_000_000,
                        "unit": "USD",
                    }
                return _fallback_tx_volume()
            except Exception as exc:
                logger.warning("Blockchain fetch_transaction_volume failed: %s", exc)
                return _fallback_tx_volume()

        return await self.fetch_cached(cache_key, _fetch, ttl=600) or _fallback_tx_volume()


def _fallback_addresses() -> dict:
    return {"values": [900000] * 30, "latest": 900000, "avg_30d": 900000}


def _fallback_hashrate() -> dict:
    return {"values": [500e18] * 30, "latest": 500e18, "avg_30d": 500e18, "unit": "EH/s"}


def _fallback_tx_volume() -> dict:
    return {"values": [5_000_000_000] * 30, "latest": 5_000_000_000, "avg_30d": 5_000_000_000, "unit": "USD"}

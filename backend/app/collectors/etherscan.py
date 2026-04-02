from __future__ import annotations
import logging
from typing import Any
from app.collectors.base import BaseCollector
from app.config import get_settings

logger = logging.getLogger(__name__)

ETHERSCAN_BASE = "https://api.etherscan.io/api"


class EtherscanCollector(BaseCollector):
    BASE_URL = ETHERSCAN_BASE

    def __init__(self) -> None:
        settings = get_settings()
        super().__init__(rate_limit=0.2, cache_ttl=120)
        self._api_key = settings.etherscan_api_key or "YourApiKeyToken"

    async def fetch(self) -> Any:
        return await self.fetch_gas_price()

    async def fetch_gas_price(self) -> dict:
        cache_key = "es_gas_price"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    self.BASE_URL,
                    params={
                        "module": "gastracker",
                        "action": "gasoracle",
                        "apikey": self._api_key,
                    },
                )
                if data and data.get("status") == "1":
                    result = data["result"]
                    return {
                        "safe_gas": float(result.get("SafeGasPrice", 20)),
                        "propose_gas": float(result.get("ProposeGasPrice", 25)),
                        "fast_gas": float(result.get("FastGasPrice", 35)),
                        "suggest_base_fee": float(result.get("suggestBaseFee", 15)),
                        "unit": "gwei",
                    }
                return _fallback_gas()
            except Exception as exc:
                logger.warning("Etherscan fetch_gas_price failed: %s", exc)
                return _fallback_gas()

        return await self.fetch_cached(cache_key, _fetch, ttl=60) or _fallback_gas()

    async def fetch_eth_supply(self) -> dict:
        cache_key = "es_eth_supply"

        async def _fetch():
            try:
                data = await self._get_with_retry(
                    self.BASE_URL,
                    params={
                        "module": "stats",
                        "action": "ethsupply2",
                        "apikey": self._api_key,
                    },
                )
                if data and data.get("status") == "1":
                    result = data["result"]
                    eth_supply = int(result.get("EthSupply", 120_000_000_000_000_000_000_000_000)) / 1e18
                    burned = int(result.get("BurntFees", 0)) / 1e18
                    return {
                        "eth_supply": eth_supply,
                        "burned_fees": burned,
                        "net_supply": eth_supply,
                    }
                return _fallback_supply()
            except Exception as exc:
                logger.warning("Etherscan fetch_eth_supply failed: %s", exc)
                return _fallback_supply()

        return await self.fetch_cached(cache_key, _fetch, ttl=3600) or _fallback_supply()

    async def fetch_transaction_count(self) -> dict:
        cache_key = "es_tx_count"

        async def _fetch():
            try:
                # Daily tx count from the stats endpoint
                data = await self._get_with_retry(
                    self.BASE_URL,
                    params={
                        "module": "stats",
                        "action": "dailytx",
                        "startdate": "2024-01-01",
                        "enddate": "2024-12-31",
                        "sort": "desc",
                        "apikey": self._api_key,
                    },
                )
                if data and data.get("status") == "1" and isinstance(data.get("result"), list):
                    records = data["result"][:30]
                    values = [int(r.get("transactionCount", 1_200_000)) for r in records]
                    return {
                        "values": values,
                        "latest": values[0] if values else 1_200_000,
                        "avg_30d": sum(values) / len(values) if values else 1_200_000,
                    }
                return _fallback_tx_count()
            except Exception as exc:
                logger.warning("Etherscan fetch_transaction_count failed: %s", exc)
                return _fallback_tx_count()

        return await self.fetch_cached(cache_key, _fetch, ttl=3600) or _fallback_tx_count()


def _fallback_gas() -> dict:
    return {"safe_gas": 20.0, "propose_gas": 25.0, "fast_gas": 35.0, "suggest_base_fee": 15.0, "unit": "gwei"}


def _fallback_supply() -> dict:
    return {"eth_supply": 120_000_000.0, "burned_fees": 3_500_000.0, "net_supply": 120_000_000.0}


def _fallback_tx_count() -> dict:
    return {"values": [1_200_000] * 30, "latest": 1_200_000, "avg_30d": 1_200_000}

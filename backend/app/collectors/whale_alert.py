from __future__ import annotations
import logging
from typing import Any
from app.collectors.base import BaseCollector
from app.config import get_settings

logger = logging.getLogger(__name__)

WHALE_ALERT_BASE = "https://api.whale-alert.io/v1/transactions"


class WhaleAlertCollector(BaseCollector):
    BASE_URL = WHALE_ALERT_BASE

    def __init__(self) -> None:
        settings = get_settings()
        super().__init__(rate_limit=0.2, cache_ttl=600)
        self._api_key = settings.whale_alert_api_key

    async def fetch(self) -> Any:
        return await self.fetch_recent_transactions()

    async def fetch_recent_transactions(self, min_value: int = 1_000_000) -> list[dict]:
        cache_key = f"whale_txns_{min_value}"

        async def _fetch():
            if not self._api_key:
                logger.debug("Whale Alert API key not set; returning simulated data")
                return _simulated_transactions()
            try:
                import time as _time
                start = int(_time.time()) - 3600
                data = await self._get_with_retry(
                    self.BASE_URL,
                    params={
                        "api_key": self._api_key,
                        "min_value": min_value,
                        "start": start,
                        "currency": "btc,eth",
                        "limit": 20,
                    },
                )
                if data and "transactions" in data:
                    txns = []
                    for t in data["transactions"]:
                        txns.append({
                            "id": t.get("id", ""),
                            "blockchain": t.get("blockchain", ""),
                            "symbol": t.get("symbol", ""),
                            "amount": float(t.get("amount", 0)),
                            "amount_usd": float(t.get("amount_usd", 0)),
                            "transaction_type": t.get("transaction_type", "transfer"),
                            "from_type": t.get("from", {}).get("owner_type", "unknown"),
                            "to_type": t.get("to", {}).get("owner_type", "unknown"),
                            "timestamp": int(t.get("timestamp", 0)),
                        })
                    return txns
                return _simulated_transactions()
            except Exception as exc:
                logger.warning("Whale Alert fetch failed: %s", exc)
                return _simulated_transactions()

        return await self.fetch_cached(cache_key, _fetch, ttl=600) or _simulated_transactions()


def _simulated_transactions() -> list[dict]:
    import time as _t
    now = int(_t.time())
    return [
        {"id": "sim1", "blockchain": "bitcoin", "symbol": "btc", "amount": 500.0, "amount_usd": 22_500_000, "transaction_type": "transfer", "from_type": "unknown", "to_type": "exchange", "timestamp": now - 1800},
        {"id": "sim2", "blockchain": "bitcoin", "symbol": "btc", "amount": 1200.0, "amount_usd": 54_000_000, "transaction_type": "transfer", "from_type": "exchange", "to_type": "unknown", "timestamp": now - 3000},
        {"id": "sim3", "blockchain": "ethereum", "symbol": "eth", "amount": 5000.0, "amount_usd": 12_000_000, "transaction_type": "transfer", "from_type": "unknown", "to_type": "unknown", "timestamp": now - 900},
    ]

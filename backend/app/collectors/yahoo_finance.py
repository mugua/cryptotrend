from __future__ import annotations
import asyncio
import logging
from typing import Any
from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

_TICKER_MAP = {
    "spx": "^GSPC",
    "vix": "^VIX",
    "dxy": "DX-Y.NYB",
    "gold": "GC=F",
}


class YahooFinanceCollector(BaseCollector):
    """Uses yfinance (sync) run in a thread executor."""

    def __init__(self) -> None:
        super().__init__(rate_limit=0.5, cache_ttl=600)

    async def fetch(self) -> Any:
        return await self.fetch_spx()

    async def _fetch_ticker(self, ticker: str, period: str = "1mo") -> dict:
        cache_key = f"yf_{ticker}_{period}"

        async def _fetch():
            try:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, _sync_fetch, ticker, period)
            except Exception as exc:
                logger.warning("Yahoo Finance fetch failed for %s: %s", ticker, exc)
                return _empty_ticker(ticker)

        return await self.fetch_cached(cache_key, _fetch, ttl=600) or _empty_ticker(ticker)

    async def fetch_spx(self) -> dict:
        return await self._fetch_ticker(_TICKER_MAP["spx"])

    async def fetch_vix(self) -> dict:
        return await self._fetch_ticker(_TICKER_MAP["vix"])

    async def fetch_dxy(self) -> dict:
        return await self._fetch_ticker(_TICKER_MAP["dxy"])

    async def fetch_gold(self) -> dict:
        return await self._fetch_ticker(_TICKER_MAP["gold"])


def _sync_fetch(ticker: str, period: str) -> dict:
    import yfinance as yf  # type: ignore

    t = yf.Ticker(ticker)
    df = t.history(period=period)
    if df is None or df.empty:
        return _empty_ticker(ticker)
    return {
        "ticker": ticker,
        "open": df["Open"].tolist(),
        "high": df["High"].tolist(),
        "low": df["Low"].tolist(),
        "close": df["Close"].tolist(),
        "volume": df["Volume"].tolist(),
        "dates": [str(d.date()) for d in df.index],
        "latest_close": float(df["Close"].iloc[-1]),
        "change_pct": float((df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2] * 100) if len(df) > 1 else 0.0,
    }


def _empty_ticker(ticker: str) -> dict:
    return {"ticker": ticker, "open": [], "high": [], "low": [], "close": [], "volume": [], "dates": [], "latest_close": 0.0, "change_pct": 0.0}

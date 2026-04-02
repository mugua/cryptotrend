from __future__ import annotations
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from app.collectors import CoinGeckoCollector, BinanceCollector
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

_cg = CoinGeckoCollector()
_bn = BinanceCollector()


@router.get("/prices")
async def get_prices():
    """Return latest prices for all tracked coins."""
    try:
        coins = await _cg.fetch_prices(settings.tracked_coins)
        result = []
        for c in coins:
            result.append({
                "coin_id": c.get("id", ""),
                "symbol": c.get("symbol", "").upper(),
                "name": c.get("name", ""),
                "price_usd": float(c.get("current_price", 0)),
                "change_24h": float(c.get("price_change_percentage_24h", 0)),
                "market_cap": float(c.get("market_cap", 0)),
                "volume_24h": float(c.get("total_volume", 0)),
                "last_updated": datetime.utcnow().isoformat(),
            })
        return {"coins": result, "last_updated": datetime.utcnow().isoformat()}
    except Exception as exc:
        logger.error("get_prices failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/kline/{symbol}")
async def get_kline(
    symbol: str,
    interval: str = Query("1d", description="Candle interval: 1m, 5m, 1h, 4h, 1d"),
    limit: int = Query(200, ge=1, le=1000),
):
    """Return K-line (OHLCV) data for a trading pair."""
    try:
        klines = await _bn.fetch_klines(symbol.upper(), interval, limit)
        return klines
    except Exception as exc:
        logger.error("get_kline failed for %s: %s", symbol, exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/overview")
async def get_market_overview():
    """Return global market overview."""
    try:
        overview = await _cg.fetch_market_overview()
        return overview
    except Exception as exc:
        logger.error("get_market_overview failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))

from __future__ import annotations
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.engine import TrendScorer

logger = logging.getLogger(__name__)
router = APIRouter()

_scorer = TrendScorer()

SUPPORTED_COINS = {
    "bitcoin", "ethereum", "binancecoin", "solana", "xrp",
    "cardano", "avalanche-2", "polkadot", "chainlink", "litecoin",
}


def _validate_coin(coin_id: str) -> None:
    if coin_id not in SUPPORTED_COINS:
        raise HTTPException(
            status_code=404,
            detail=f"Coin '{coin_id}' not supported. Supported: {sorted(SUPPORTED_COINS)}",
        )


@router.get("/trend-score/{coin_id}")
async def get_trend_score(coin_id: str):
    """Calculate and return full trend score for a coin."""
    _validate_coin(coin_id)
    try:
        analysis = await _scorer.generate_full_analysis(coin_id)
        return {
            "coin_id": coin_id,
            "coin_name": analysis.get("coin_name", coin_id.title()),
            "overall_score": analysis["overall_score"],
            "trend_level": analysis["trend_level"],
            "technical_score": analysis["technical"]["score"],
            "onchain_score": analysis["onchain"]["score"],
            "sentiment_score": analysis["sentiment"]["score"],
            "macro_score": analysis["macro"]["score"],
            "market_structure_score": analysis["market_structure"]["score"],
            "factor_scores": analysis.get("factor_scores", []),
            "timestamp": analysis.get("timestamp", datetime.utcnow().isoformat()),
            "summary": f"{analysis.get('coin_name', coin_id.title())} shows a {analysis['trend_level']} trend (score: {analysis['overall_score']:.1f}/100)",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_trend_score failed for %s: %s", coin_id, exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/factors/{coin_id}")
async def get_factors(coin_id: str):
    """Return all factor details for a coin."""
    _validate_coin(coin_id)
    try:
        analysis = await _scorer.generate_full_analysis(coin_id)
        return {
            "coin_id": coin_id,
            "overall_score": analysis["overall_score"],
            "trend_level": analysis["trend_level"],
            "technical": analysis["technical"],
            "onchain": analysis["onchain"],
            "sentiment": analysis["sentiment"],
            "macro": analysis["macro"],
            "market_structure": analysis["market_structure"],
            "timestamp": analysis.get("timestamp"),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_factors failed for %s: %s", coin_id, exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/technical/{coin_id}")
async def get_technical(coin_id: str):
    """Return technical analysis factor details."""
    _validate_coin(coin_id)
    try:
        from app.collectors import BinanceCollector
        from app.engine import TechnicalAnalyzer

        symbol_map = {
            "bitcoin": "BTCUSDT", "ethereum": "ETHUSDT", "binancecoin": "BNBUSDT",
            "solana": "SOLUSDT", "xrp": "XRPUSDT", "cardano": "ADAUSDT",
            "avalanche-2": "AVAXUSDT", "polkadot": "DOTUSDT",
            "chainlink": "LINKUSDT", "litecoin": "LTCUSDT",
        }
        symbol = symbol_map.get(coin_id, "BTCUSDT")
        bn = BinanceCollector()
        klines = await bn.fetch_klines(symbol, "1d", 200)
        analyzer = TechnicalAnalyzer()
        result = analyzer.score_technical(klines)
        return {"coin_id": coin_id, "symbol": symbol, **result}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_technical failed for %s: %s", coin_id, exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/onchain/{coin_id}")
async def get_onchain(coin_id: str):
    """Return on-chain factor details."""
    _validate_coin(coin_id)
    try:
        from app.collectors import BlockchainCollector, EtherscanCollector, WhaleAlertCollector
        from app.engine import OnchainAnalyzer

        bc = BlockchainCollector()
        es = EtherscanCollector()
        wh = WhaleAlertCollector()
        import asyncio
        addr, hr, gas, whale = await asyncio.gather(
            bc.fetch_active_addresses(),
            bc.fetch_hash_rate(),
            es.fetch_gas_price(),
            wh.fetch_recent_transactions(),
            return_exceptions=True,
        )
        collectors_data = {
            "active_addresses": addr if not isinstance(addr, Exception) else {},
            "hash_rate": hr if not isinstance(hr, Exception) else {},
            "gas_price": gas if not isinstance(gas, Exception) else {},
            "whale_transactions": whale if not isinstance(whale, Exception) else [],
            "exchange_flow": {"inflow": 800, "outflow": 1000},
        }
        analyzer = OnchainAnalyzer()
        result = analyzer.score_onchain(coin_id, collectors_data)
        return {"coin_id": coin_id, **result}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_onchain failed for %s: %s", coin_id, exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/sentiment/{coin_id}")
async def get_sentiment(coin_id: str):
    """Return sentiment factor details."""
    _validate_coin(coin_id)
    try:
        from app.collectors import (
            FearGreedCollector, RedditCollector, GoogleTrendsCollector,
            BinanceCollector,
        )
        from app.engine import SentimentAnalyzer
        import asyncio

        symbol_map = {"bitcoin": "BTCUSDT", "ethereum": "ETHUSDT"}
        symbol = symbol_map.get(coin_id, "BTCUSDT")
        keyword_map = {"bitcoin": "bitcoin", "ethereum": "ethereum"}
        keyword = keyword_map.get(coin_id, coin_id)

        fg = FearGreedCollector()
        rd = RedditCollector()
        gt = GoogleTrendsCollector()
        bn = BinanceCollector()

        fg_data, reddit_btc, reddit_eth, trends, funding, ls = await asyncio.gather(
            fg.fetch_current(),
            rd.fetch_subreddit_stats("bitcoin"),
            rd.fetch_subreddit_stats("ethereum"),
            gt.fetch_trends(keyword),
            bn.fetch_funding_rate(symbol),
            bn.fetch_long_short_ratio(symbol),
            return_exceptions=True,
        )

        sentiment_data = {
            "fear_greed": fg_data if not isinstance(fg_data, Exception) else {"value": 50},
            "social": {
                "bitcoin": reddit_btc if not isinstance(reddit_btc, Exception) else {},
                "ethereum": reddit_eth if not isinstance(reddit_eth, Exception) else {},
            },
            "google_trends": trends if not isinstance(trends, Exception) else {},
            "funding_rate": float(funding.get("funding_rate", 0.0001)) if not isinstance(funding, Exception) else 0.0001,
            "long_short_ratio": float(ls.get("long_short_ratio", 1.0)) if not isinstance(ls, Exception) else 1.0,
        }
        analyzer = SentimentAnalyzer()
        result = analyzer.score_sentiment(sentiment_data)
        return {"coin_id": coin_id, **result}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_sentiment failed for %s: %s", coin_id, exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/macro")
async def get_macro():
    """Return macro economic factor details."""
    try:
        from app.collectors import FREDCollector, YahooFinanceCollector
        from app.engine import MacroAnalyzer
        import asyncio

        fred = FREDCollector()
        yf = YahooFinanceCollector()

        dxy, yield_d, vix, m2, spx = await asyncio.gather(
            fred.fetch_dxy(),
            fred.fetch_treasury_yield(),
            fred.fetch_vix(),
            fred.fetch_m2(),
            yf.fetch_spx(),
            return_exceptions=True,
        )

        macro_data = {
            "dxy": dxy if not isinstance(dxy, Exception) else {},
            "treasury_yield": yield_d if not isinstance(yield_d, Exception) else {},
            "vix": vix if not isinstance(vix, Exception) else {},
            "m2": m2 if not isinstance(m2, Exception) else {},
            "spx_closes": (spx.get("close", []) if not isinstance(spx, Exception) else []),
            "crypto_closes": [],
        }
        analyzer = MacroAnalyzer()
        result = analyzer.score_macro(macro_data)
        return result
    except Exception as exc:
        logger.error("get_macro failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/market-structure")
async def get_market_structure():
    """Return market structure factor details."""
    try:
        from app.collectors import CoinGeckoCollector, BinanceCollector
        from app.engine import MarketStructureAnalyzer
        import asyncio

        cg = CoinGeckoCollector()
        bn = BinanceCollector()

        overview, btc_klines, eth_klines, btc_oi = await asyncio.gather(
            cg.fetch_market_overview(),
            bn.fetch_klines("BTCUSDT", "1d", 30),
            bn.fetch_klines("ETHUSDT", "1d", 1),
            bn.fetch_open_interest("BTCUSDT"),
            return_exceptions=True,
        )

        btc_closes = (btc_klines.get("close", []) if not isinstance(btc_klines, Exception) else [])
        eth_closes = (eth_klines.get("close", []) if not isinstance(eth_klines, Exception) else [])
        btc_volumes = (btc_klines.get("volume", []) if not isinstance(btc_klines, Exception) else [])
        oi = btc_oi if not isinstance(btc_oi, Exception) else {}

        btc_price = btc_closes[-1] if btc_closes else 45000.0
        eth_price = eth_closes[-1] if eth_closes else 2400.0
        current_vol = btc_volumes[-1] if btc_volumes else 80e9
        avg_vol = sum(btc_volumes[-30:]) / len(btc_volumes[-30:]) if len(btc_volumes) >= 30 else current_vol

        overview_d = overview if not isinstance(overview, Exception) else {}
        ms_data = {
            "btc_dominance": overview_d.get("btc_dominance", 52.0),
            "stablecoin": {"current": overview_d.get("stablecoin_market_cap", 140e9), "prev_30d": overview_d.get("stablecoin_market_cap", 140e9) * 0.98},
            "open_interest": {"open_interest": float(oi.get("open_interest", 10e9)), "prev": float(oi.get("open_interest", 10e9)) * 0.95, "price_change_pct": 0.0},
            "eth_price": eth_price,
            "btc_price": btc_price,
            "volume": {"current_volume": current_vol, "avg_volume_30d": avg_vol, "price_change_pct": 0.0},
        }
        analyzer = MarketStructureAnalyzer()
        result = analyzer.score_market_structure(ms_data)
        return result
    except Exception as exc:
        logger.error("get_market_structure failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))

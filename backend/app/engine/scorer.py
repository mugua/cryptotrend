from __future__ import annotations
import logging
from datetime import datetime

from app.engine.weights import FACTOR_WEIGHTS, SCORE_LEVELS
from app.engine.technical import TechnicalAnalyzer
from app.engine.onchain import OnchainAnalyzer
from app.engine.sentiment import SentimentAnalyzer
from app.engine.macro import MacroAnalyzer
from app.engine.market_structure import MarketStructureAnalyzer

logger = logging.getLogger(__name__)

_technical = TechnicalAnalyzer()
_onchain = OnchainAnalyzer()
_sentiment = SentimentAnalyzer()
_macro = MacroAnalyzer()
_market_structure = MarketStructureAnalyzer()


class TrendScorer:
    """Aggregates all factor scores into a single trend score."""

    WEIGHTS = FACTOR_WEIGHTS

    def calculate_overall_score(self, scores: dict) -> float:
        total = 0.0
        for factor, weight in self.WEIGHTS.items():
            total += scores.get(factor, 50.0) * weight
        return round(total, 2)

    @staticmethod
    def get_trend_level(score: float) -> str:
        for (low, high), label in SCORE_LEVELS.items():
            if low <= score <= high:
                return label
        return "Neutral"

    async def generate_full_analysis(self, coin_id: str) -> dict:
        """
        Collect data from all sources and generate a complete analysis.
        Returns a dict with all factor details and overall trend score.
        """
        from app.collectors import (
            CoinGeckoCollector,
            BinanceCollector,
            BlockchainCollector,
            EtherscanCollector,
            FearGreedCollector,
            FREDCollector,
            RedditCollector,
            GoogleTrendsCollector,
            WhaleAlertCollector,
            YahooFinanceCollector,
        )

        symbol_map = {
            "bitcoin": "BTCUSDT",
            "ethereum": "ETHUSDT",
            "binancecoin": "BNBUSDT",
            "solana": "SOLUSDT",
            "xrp": "XRPUSDT",
            "cardano": "ADAUSDT",
            "avalanche-2": "AVAXUSDT",
            "polkadot": "DOTUSDT",
            "chainlink": "LINKUSDT",
            "litecoin": "LTCUSDT",
        }
        symbol = symbol_map.get(coin_id, "BTCUSDT")
        keyword_map = {
            "bitcoin": "bitcoin",
            "ethereum": "ethereum",
        }
        keyword = keyword_map.get(coin_id, coin_id)

        # ── Instantiate collectors ─────────────────────────────────────────
        cg = CoinGeckoCollector()
        bn = BinanceCollector()
        bc = BlockchainCollector()
        es = EtherscanCollector()
        fg = FearGreedCollector()
        fred = FREDCollector()
        rd = RedditCollector()
        gt = GoogleTrendsCollector()
        wh = WhaleAlertCollector()
        yf = YahooFinanceCollector()

        # ── Fetch data concurrently ─────────────────────────────────────────
        import asyncio
        (
            klines,
            coin_prices,
            overview,
            bc_addresses,
            bc_hashrate,
            es_gas,
            fear_greed_data,
            fred_dxy,
            fred_yield,
            fred_vix,
            fred_m2,
            reddit_btc,
            reddit_eth,
            trends_data,
            whale_txns,
            yf_spx,
            funding_data,
            oi_data,
            ls_data,
        ) = await asyncio.gather(
            bn.fetch_klines(symbol, "1d", 200),
            cg.fetch_prices([coin_id]),
            cg.fetch_market_overview(),
            bc.fetch_active_addresses(),
            bc.fetch_hash_rate(),
            es.fetch_gas_price(),
            fg.fetch_current(),
            fred.fetch_dxy(),
            fred.fetch_treasury_yield(),
            fred.fetch_vix(),
            fred.fetch_m2(),
            rd.fetch_subreddit_stats("bitcoin"),
            rd.fetch_subreddit_stats("ethereum"),
            gt.fetch_trends(keyword),
            wh.fetch_recent_transactions(),
            yf.fetch_spx(),
            bn.fetch_funding_rate(symbol),
            bn.fetch_open_interest(symbol),
            bn.fetch_long_short_ratio(symbol),
            return_exceptions=False,
        )

        # ── Current coin price ─────────────────────────────────────────────
        coin_info = coin_prices[0] if coin_prices else {}
        current_price = float(coin_info.get("current_price", 0))
        price_change_24h = float(coin_info.get("price_change_percentage_24h", 0))

        # ── Technical Score ────────────────────────────────────────────────
        tech_result = _technical.score_technical(klines)

        # ── On-chain Score ─────────────────────────────────────────────────
        onchain_collectors = {
            "active_addresses": bc_addresses,
            "hash_rate": bc_hashrate,
            "gas_price": es_gas,
            "whale_transactions": whale_txns,
            "exchange_flow": {"inflow": 800, "outflow": 1000},
        }
        onchain_result = _onchain.score_onchain(coin_id, onchain_collectors)

        # ── Sentiment Score ────────────────────────────────────────────────
        sentiment_data = {
            "fear_greed": fear_greed_data,
            "social": {
                "bitcoin": reddit_btc,
                "ethereum": reddit_eth,
            },
            "google_trends": trends_data,
            "funding_rate": float(funding_data.get("funding_rate", 0.0001)),
            "long_short_ratio": float(ls_data.get("long_short_ratio", 1.0)),
        }
        sentiment_result = _sentiment.score_sentiment(sentiment_data)

        # ── Macro Score ────────────────────────────────────────────────────
        spx_closes = yf_spx.get("close", [])
        crypto_closes = klines.get("close", [])
        macro_data = {
            "dxy": fred_dxy,
            "treasury_yield": fred_yield,
            "vix": fred_vix,
            "m2": fred_m2,
            "spx_closes": spx_closes,
            "crypto_closes": crypto_closes,
        }
        macro_result = _macro.score_macro(macro_data)

        # ── Market Structure Score ─────────────────────────────────────────
        eth_price = 2400.0
        btc_price = 45000.0
        if coin_id == "ethereum":
            eth_price = current_price or eth_price
        elif coin_id == "bitcoin":
            btc_price = current_price or btc_price

        volumes = klines.get("volume", [])
        current_vol = volumes[-1] if volumes else 80e9
        avg_vol = sum(volumes[-30:]) / len(volumes[-30:]) if len(volumes) >= 30 else current_vol

        ms_data = {
            "btc_dominance": overview.get("btc_dominance", 52.0),
            "stablecoin": {
                "current": overview.get("stablecoin_market_cap", 140e9),
                "prev_30d": overview.get("stablecoin_market_cap", 140e9) * 0.98,
            },
            "open_interest": {
                "open_interest": float(oi_data.get("open_interest", 10e9)),
                "prev": float(oi_data.get("open_interest", 10e9)) * 0.95,
                "price_change_pct": price_change_24h,
            },
            "eth_price": eth_price,
            "btc_price": btc_price,
            "volume": {
                "current_volume": current_vol,
                "avg_volume_30d": avg_vol,
                "price_change_pct": price_change_24h,
            },
        }
        ms_result = _market_structure.score_market_structure(ms_data)

        # ── Overall Score ──────────────────────────────────────────────────
        factor_scores = {
            "technical": tech_result["score"],
            "onchain": onchain_result["score"],
            "sentiment": sentiment_result["score"],
            "macro": macro_result["score"],
            "market_structure": ms_result["score"],
        }
        overall = self.calculate_overall_score(factor_scores)
        trend_level = self.get_trend_level(overall)

        # ── Build factor score list ────────────────────────────────────────
        def _signal(s: float) -> str:
            if s >= 60:
                return "bullish"
            elif s <= 40:
                return "bearish"
            return "neutral"

        factor_score_list = [
            {
                "name": k,
                "score": v,
                "weight": self.WEIGHTS[k],
                "weighted_score": round(v * self.WEIGHTS[k], 4),
                "signal": _signal(v),
                "details": {},
            }
            for k, v in factor_scores.items()
        ]

        return {
            "coin_id": coin_id,
            "coin_name": coin_info.get("name", coin_id.title()),
            "overall_score": overall,
            "trend_level": trend_level,
            "factor_scores": factor_score_list,
            "technical": tech_result,
            "onchain": onchain_result,
            "sentiment": sentiment_result,
            "macro": macro_result,
            "market_structure": ms_result,
            "current_price": current_price,
            "price_change_24h": price_change_24h,
            "timestamp": datetime.utcnow().isoformat(),
        }

from __future__ import annotations
from app.engine.weights import MARKET_STRUCTURE_WEIGHTS


class MarketStructureAnalyzer:
    """Market structure factor analysis and scoring."""

    @staticmethod
    def analyze_btc_dominance(value: float) -> dict:
        # BTC dominance rising with price = healthy bull market
        # Very high dominance = altcoins weak; very low = altseason
        if value >= 60:
            score = 70.0
            signal = "btc_season"
        elif value >= 50:
            score = 60.0
            signal = "btc_favored"
        elif value >= 45:
            score = 55.0
            signal = "balanced"
        elif value >= 40:
            score = 50.0
            signal = "alt_favored"
        else:
            score = 40.0
            signal = "alt_season"

        return {"score": round(score, 2), "signal": signal, "btc_dominance_pct": round(value, 2)}

    @staticmethod
    def analyze_stablecoin_supply(data: dict) -> dict:
        # Growing stablecoin supply = more dry powder on sidelines = bullish
        current = float(data.get("current", 140e9))
        prev = float(data.get("prev_30d", 138e9))

        if prev == 0:
            chg_pct = 0.0
        else:
            chg_pct = (current - prev) / prev * 100

        if chg_pct > 5:
            score = 75.0
        elif chg_pct > 2:
            score = 65.0
        elif chg_pct > 0:
            score = 55.0
        elif chg_pct > -2:
            score = 45.0
        else:
            score = 35.0

        return {
            "score": round(score, 2),
            "change_pct": round(chg_pct, 2),
            "current_bn_usd": round(current / 1e9, 2),
            "signal": "bullish" if chg_pct > 2 else "bearish" if chg_pct < -2 else "neutral",
        }

    @staticmethod
    def analyze_open_interest(data: dict) -> dict:
        current = float(data.get("open_interest", 10e9))
        prev = float(data.get("prev", 9.5e9))
        price_change = float(data.get("price_change_pct", 0.0))

        if prev == 0:
            oi_chg = 0.0
        else:
            oi_chg = (current - prev) / prev * 100

        # Rising OI + rising price = healthy trend
        # Rising OI + falling price = bearish divergence
        if oi_chg > 5 and price_change > 0:
            score = 75.0
            signal = "bullish_expansion"
        elif oi_chg > 5 and price_change < 0:
            score = 30.0
            signal = "bearish_expansion"
        elif oi_chg < -5 and price_change > 0:
            score = 60.0
            signal = "short_squeeze"
        elif oi_chg < -5 and price_change < 0:
            score = 40.0
            signal = "capitulation"
        else:
            score = 50.0
            signal = "neutral"

        return {
            "score": round(score, 2),
            "signal": signal,
            "oi_change_pct": round(oi_chg, 2),
            "current": current,
        }

    @staticmethod
    def analyze_eth_btc_ratio(ratio: float) -> dict:
        # ETH/BTC ratio indicates relative strength
        # Rising ratio = ETH outperforming = altcoin season signal
        if ratio > 0.08:
            score = 70.0
            signal = "eth_strong"
        elif ratio > 0.06:
            score = 60.0
            signal = "eth_neutral_high"
        elif ratio > 0.04:
            score = 55.0
            signal = "balanced"
        elif ratio > 0.02:
            score = 45.0
            signal = "btc_favored"
        else:
            score = 35.0
            signal = "btc_dominant"

        return {"score": round(score, 2), "signal": signal, "ratio": round(ratio, 6)}

    @staticmethod
    def analyze_volume_change(data: dict) -> dict:
        current_vol = float(data.get("current_volume", 80e9))
        avg_vol = float(data.get("avg_volume_30d", 70e9))
        price_change = float(data.get("price_change_pct", 0.0))

        if avg_vol == 0:
            ratio = 1.0
        else:
            ratio = current_vol / avg_vol

        # High volume confirming price move is bullish
        if ratio > 1.5 and price_change > 0:
            score = 80.0
            signal = "strong_bullish_volume"
        elif ratio > 1.2 and price_change > 0:
            score = 65.0
            signal = "bullish_volume"
        elif ratio > 1.2 and price_change < 0:
            score = 30.0
            signal = "bearish_volume"
        elif ratio < 0.8:
            score = 45.0
            signal = "low_volume"
        else:
            score = 50.0
            signal = "average_volume"

        return {
            "score": round(score, 2),
            "signal": signal,
            "ratio_vs_avg": round(ratio, 4),
            "current_volume_bn": round(current_vol / 1e9, 2),
        }

    def score_market_structure(self, data: dict) -> dict:
        w = MARKET_STRUCTURE_WEIGHTS

        btc_dom = float(data.get("btc_dominance", 52.0))
        btc_result = self.analyze_btc_dominance(btc_dom)

        stable_data = data.get("stablecoin", {"current": 140e9, "prev_30d": 138e9})
        stable_result = self.analyze_stablecoin_supply(stable_data)

        oi_data = data.get("open_interest", {})
        oi_result = self.analyze_open_interest(oi_data)

        eth_price = float(data.get("eth_price", 2400))
        btc_price = float(data.get("btc_price", 45000))
        eth_btc = (eth_price / btc_price) if btc_price > 0 else 0.05
        eth_btc_result = self.analyze_eth_btc_ratio(eth_btc)

        vol_data = data.get("volume", {"current_volume": 80e9, "avg_volume_30d": 70e9, "price_change_pct": 0.0})
        vol_result = self.analyze_volume_change(vol_data)

        composite = (
            btc_result["score"] * w["btc_dominance"]
            + stable_result["score"] * w["stablecoin"]
            + oi_result["score"] * w["open_interest"]
            + eth_btc_result["score"] * w["eth_btc_ratio"]
            + vol_result["score"] * w["volume"]
        )

        return {
            "score": round(composite, 2),
            "btc_dominance": btc_result,
            "stablecoin": stable_result,
            "open_interest": oi_result,
            "eth_btc_ratio": eth_btc_result,
            "volume": vol_result,
        }

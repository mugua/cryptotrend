from __future__ import annotations
import math
from app.engine.weights import MACRO_WEIGHTS


class MacroAnalyzer:
    """Macro-economic factor analysis and scoring."""

    @staticmethod
    def calculate_correlation(series1: list[float], series2: list[float]) -> float:
        n = min(len(series1), len(series2))
        if n < 2:
            return 0.0
        s1 = series1[-n:]
        s2 = series2[-n:]
        mean1 = sum(s1) / n
        mean2 = sum(s2) / n
        cov = sum((s1[i] - mean1) * (s2[i] - mean2) for i in range(n)) / n
        std1 = math.sqrt(sum((x - mean1) ** 2 for x in s1) / n)
        std2 = math.sqrt(sum((x - mean2) ** 2 for x in s2) / n)
        if std1 == 0 or std2 == 0:
            return 0.0
        return cov / (std1 * std2)

    @staticmethod
    def analyze_dxy(data: dict) -> dict:
        values = data.get("values", [104.0])
        latest = float(data.get("latest", 104.0))
        avg = float(data.get("avg_30d", 104.0))

        # DXY is negatively correlated with crypto
        # High DXY (strong dollar) → bearish for crypto
        # Low/falling DXY → bullish for crypto
        if avg == 0:
            ratio = 1.0
        else:
            ratio = latest / avg

        # Trend: falling DXY = bullish
        if len(values) >= 5:
            recent5 = sum(values[-5:]) / 5
            prior5 = sum(values[-10:-5]) / 5 if len(values) >= 10 else avg
            trend_chg = (recent5 - prior5) / max(prior5, 1)
        else:
            trend_chg = 0.0

        base_score = 100 - (latest - 90) * 2  # 90 DXY → 80, 110 DXY → 40
        base_score = max(20.0, min(80.0, base_score))
        # Adjust for trend: falling = +10, rising = -10
        trend_adj = -trend_chg * 500
        score = max(0.0, min(100.0, base_score + trend_adj))

        return {
            "score": round(score, 2),
            "latest": latest,
            "avg_30d": avg,
            "trend_change": round(trend_chg * 100, 4),
            "impact": "bearish" if latest > 105 else "bullish" if latest < 100 else "neutral",
        }

    @staticmethod
    def analyze_treasury_yield(data: dict) -> dict:
        latest = float(data.get("latest", 4.5))
        avg = float(data.get("avg_30d", 4.5))

        # Higher yields = more attractive risk-free rate = bearish for crypto
        if latest > 5.5:
            score = 25.0
        elif latest > 4.5:
            score = 35.0
        elif latest > 3.5:
            score = 50.0
        elif latest > 2.5:
            score = 65.0
        else:
            score = 75.0

        # Trend adjustment
        if avg > 0:
            chg = (latest - avg) / avg
            score = max(0.0, min(100.0, score - chg * 200))

        return {
            "score": round(score, 2),
            "latest": latest,
            "avg_30d": avg,
            "impact": "bearish" if latest > 4.5 else "bullish" if latest < 3.0 else "neutral",
        }

    @staticmethod
    def analyze_vix(data: dict) -> dict:
        latest = float(data.get("latest", 18.0))
        avg = float(data.get("avg_30d", 18.0))

        # High VIX = high fear = risk-off = bearish crypto
        # Low VIX = calm markets = risk-on = bullish
        if latest > 40:
            score = 15.0
        elif latest > 30:
            score = 30.0
        elif latest > 20:
            score = 50.0
        elif latest > 15:
            score = 65.0
        else:
            score = 75.0

        # Spike detection: sudden VIX rise = more bearish
        if avg > 0 and latest > avg * 1.3:
            score = max(0.0, score - 15)

        return {
            "score": round(score, 2),
            "latest": latest,
            "avg_30d": avg,
            "fear_level": "extreme" if latest > 40 else "high" if latest > 30 else "moderate" if latest > 20 else "low",
        }

    @staticmethod
    def analyze_m2_supply(data: dict) -> dict:
        yoy_change = float(data.get("yoy_change_pct", 2.0))
        latest = float(data.get("latest", 21000.0))

        # M2 expansion = more liquidity = bullish for risk assets
        if yoy_change > 8:
            score = 80.0
        elif yoy_change > 4:
            score = 65.0
        elif yoy_change > 0:
            score = 55.0
        elif yoy_change > -2:
            score = 45.0
        else:
            score = 30.0

        return {
            "score": round(score, 2),
            "yoy_change_pct": round(yoy_change, 2),
            "latest_bn_usd": round(latest, 1),
            "impact": "bullish" if yoy_change > 4 else "bearish" if yoy_change < 0 else "neutral",
        }

    def score_macro(self, data: dict) -> dict:
        w = MACRO_WEIGHTS

        dxy_result = self.analyze_dxy(data.get("dxy", {}))
        yield_result = self.analyze_treasury_yield(data.get("treasury_yield", {}))
        vix_result = self.analyze_vix(data.get("vix", {}))
        m2_result = self.analyze_m2_supply(data.get("m2", {}))

        # Correlation with SPX (optional enrichment)
        spx_closes = data.get("spx_closes", [])
        crypto_closes = data.get("crypto_closes", [])
        corr = self.calculate_correlation(spx_closes, crypto_closes) if spx_closes and crypto_closes else 0.0

        composite = (
            dxy_result["score"] * w["dxy"]
            + yield_result["score"] * w["treasury_yield"]
            + vix_result["score"] * w["vix"]
            + m2_result["score"] * w["m2"]
        )

        return {
            "score": round(composite, 2),
            "dxy": dxy_result,
            "treasury_yield": yield_result,
            "vix": vix_result,
            "m2": m2_result,
            "correlation_spx": round(corr, 4),
        }

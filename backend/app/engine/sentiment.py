from __future__ import annotations
from app.engine.weights import SENTIMENT_WEIGHTS


class SentimentAnalyzer:
    """Sentiment factor analysis and scoring."""

    @staticmethod
    def analyze_fear_greed(value: int) -> dict:
        v = max(0, min(100, int(value)))
        # Transform: extreme fear (0) → high score (bullish contrarian),
        # extreme greed (100) → low score (bearish contrarian)
        # Fear <25 → 75-100, Greed >75 → 0-25, Neutral 45-55 → 45-55
        if v <= 25:
            score = 75.0 + (25 - v) * 1.0
        elif v <= 45:
            score = 55.0 + (45 - v) * (20.0 / 20.0)
        elif v <= 55:
            score = 50.0 + (55 - v) * (5.0 / 10.0)
        elif v <= 75:
            score = 50.0 - (v - 55) * (20.0 / 20.0)
        else:
            score = 30.0 - (v - 75) * 1.2

        score = max(0.0, min(100.0, score))

        if v <= 24:
            classification = "Extreme Fear"
        elif v <= 44:
            classification = "Fear"
        elif v <= 55:
            classification = "Neutral"
        elif v <= 74:
            classification = "Greed"
        else:
            classification = "Extreme Greed"

        return {
            "score": round(score, 2),
            "raw_value": v,
            "classification": classification,
            "contrarian_signal": "buy" if v < 30 else "sell" if v > 70 else "hold",
        }

    @staticmethod
    def analyze_social_sentiment(data: dict) -> dict:
        # data: {"bitcoin": {subscribers, active_users}, "ethereum": {…}}
        # Use active_user ratio (active/subscribers) as engagement metric
        total_score = 0.0
        count = 0
        for subreddit, stats in data.items():
            subscribers = max(1, int(stats.get("subscribers", 1)))
            active = int(stats.get("active_users", 0))
            engagement = active / subscribers * 10000  # per 10k subscribers

            # Benchmark engagement ratios
            if engagement >= 20:
                s = 80.0
            elif engagement >= 10:
                s = 65.0
            elif engagement >= 5:
                s = 50.0
            elif engagement >= 2:
                s = 35.0
            else:
                s = 25.0
            total_score += s
            count += 1

        score = total_score / count if count > 0 else 50.0
        return {"score": round(score, 2), "subreddits_analyzed": count}

    @staticmethod
    def analyze_google_trends(data: dict) -> dict:
        latest = int(data.get("latest", 50))
        avg = int(data.get("avg", 50))
        max_val = int(data.get("max", 100))

        # Normalize latest vs average
        if avg == 0:
            ratio = 1.0
        else:
            ratio = latest / avg

        # Absolute interest level (relative to historic max)
        abs_level = latest / max(max_val, 1)

        score = 40.0 + ratio * 10.0 + abs_level * 20.0
        score = max(0.0, min(100.0, score))

        return {
            "score": round(score, 2),
            "latest": latest,
            "avg": avg,
            "ratio_vs_avg": round(ratio, 4),
        }

    @staticmethod
    def analyze_funding_rate(rate: float) -> dict:
        # Positive funding rate = longs paying shorts → market is long-heavy → slightly bearish
        # Negative funding rate = shorts paying longs → market is short-heavy → bullish
        rate_pct = rate * 100

        if rate_pct < -0.05:
            score = 80.0
            signal = "extreme_negative"
        elif rate_pct < 0:
            score = 65.0
            signal = "negative"
        elif rate_pct < 0.02:
            score = 55.0
            signal = "slightly_positive"
        elif rate_pct < 0.05:
            score = 45.0
            signal = "positive"
        elif rate_pct < 0.10:
            score = 35.0
            signal = "high_positive"
        else:
            score = 20.0
            signal = "extreme_positive"

        return {"score": round(score, 2), "signal": signal, "rate_pct": round(rate_pct, 4)}

    @staticmethod
    def analyze_long_short_ratio(ratio: float) -> dict:
        # ratio = longs / shorts
        # ratio > 1 → more longs → crowded, slightly bearish contrarian
        # ratio < 1 → more shorts → contrarian bullish
        if ratio <= 0:
            return {"score": 50.0, "signal": "neutral", "ratio": 1.0}

        if ratio < 0.8:
            score = 75.0
            signal = "short_heavy_bullish"
        elif ratio < 1.0:
            score = 60.0
            signal = "slightly_short_heavy"
        elif ratio < 1.2:
            score = 50.0
            signal = "balanced"
        elif ratio < 1.5:
            score = 40.0
            signal = "slightly_long_heavy"
        else:
            score = 25.0
            signal = "long_heavy_bearish"

        return {"score": round(score, 2), "signal": signal, "ratio": round(ratio, 4)}

    def score_sentiment(self, data: dict) -> dict:
        w = SENTIMENT_WEIGHTS

        fg_data = data.get("fear_greed", {"value": 50})
        fg_result = self.analyze_fear_greed(fg_data.get("value", 50))

        social_data = data.get("social", {})
        social_result = self.analyze_social_sentiment(social_data)

        trends_data = data.get("google_trends", {})
        trends_result = self.analyze_google_trends(trends_data)

        funding_rate = float(data.get("funding_rate", 0.0001))
        funding_result = self.analyze_funding_rate(funding_rate)

        ls_ratio = float(data.get("long_short_ratio", 1.0))
        ls_result = self.analyze_long_short_ratio(ls_ratio)

        composite = (
            fg_result["score"] * w["fear_greed"]
            + social_result["score"] * w["social"]
            + trends_result["score"] * w["google_trends"]
            + funding_result["score"] * w["funding_rate"]
            + ls_result["score"] * w["long_short"]
        )

        return {
            "score": round(composite, 2),
            "fear_greed": fg_result,
            "social": social_result,
            "google_trends": trends_result,
            "funding_rate": funding_result,
            "long_short": ls_result,
        }

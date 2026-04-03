from __future__ import annotations
import math
from typing import Any
from app.engine.weights import TECHNICAL_WEIGHTS


class TechnicalAnalyzer:
    """Technical indicator calculations and scoring."""

    # ------------------------------------------------------------------ MAs

    @staticmethod
    def calculate_ma(prices: list[float], periods: list[int] = None) -> dict[str, float]:
        if periods is None:
            periods = [5, 10, 20, 50, 200]
        result: dict[str, float] = {}
        for p in periods:
            if len(prices) >= p:
                result[f"ma{p}"] = sum(prices[-p:]) / p
        return result

    @staticmethod
    def calculate_ema(prices: list[float], periods: list[int] = None) -> dict[str, float]:
        if periods is None:
            periods = [12, 26]
        result: dict[str, float] = {}
        for period in periods:
            if len(prices) < period:
                continue
            k = 2 / (period + 1)
            ema = sum(prices[:period]) / period  # seed with SMA
            for price in prices[period:]:
                ema = price * k + ema * (1 - k)
            result[f"ema{period}"] = ema
        return result

    @staticmethod
    def calculate_rsi(prices: list[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50.0
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0.0 for d in deltas]
        losses = [-d if d < 0 else 0.0 for d in deltas]

        # Wilder's smoothed average
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    @staticmethod
    def calculate_macd(
        prices: list[float],
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> dict[str, float]:
        if len(prices) < slow + signal:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}

        def _ema(data: list[float], n: int) -> list[float]:
            k = 2 / (n + 1)
            emas = [sum(data[:n]) / n]
            for p in data[n:]:
                emas.append(p * k + emas[-1] * (1 - k))
            return emas

        ema_fast = _ema(prices, fast)
        ema_slow = _ema(prices, slow)

        # Align lengths
        offset = slow - fast
        macd_line = [ema_fast[i + offset] - ema_slow[i] for i in range(len(ema_slow))]

        if len(macd_line) < signal:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}

        k_sig = 2 / (signal + 1)
        sig_val = sum(macd_line[:signal]) / signal
        for v in macd_line[signal:]:
            sig_val = v * k_sig + sig_val * (1 - k_sig)

        macd_val = macd_line[-1]
        hist = macd_val - sig_val
        return {"macd": macd_val, "signal": sig_val, "histogram": hist}

    @staticmethod
    def calculate_bollinger(
        prices: list[float], period: int = 20, std_multiplier: float = 2.0
    ) -> dict[str, float]:
        if len(prices) < period:
            mid = prices[-1] if prices else 0.0
            return {"upper": mid * 1.05, "middle": mid, "lower": mid * 0.95, "pct_b": 0.5}
        window = prices[-period:]
        middle = sum(window) / period
        variance = sum((p - middle) ** 2 for p in window) / period
        std = math.sqrt(variance)
        upper = middle + std_multiplier * std
        lower = middle - std_multiplier * std
        latest = prices[-1]
        band_width = upper - lower
        pct_b = (latest - lower) / band_width if band_width != 0 else 0.5
        return {"upper": upper, "middle": middle, "lower": lower, "pct_b": pct_b}

    @staticmethod
    def calculate_volatility(prices: list[float], period: int = 30) -> float:
        if len(prices) < 2:
            return 0.0
        window = prices[-min(period, len(prices)):]
        returns = [(window[i] - window[i - 1]) / window[i - 1] for i in range(1, len(window)) if window[i - 1] != 0]
        if not returns:
            return 0.0
        mean_r = sum(returns) / len(returns)
        variance = sum((r - mean_r) ** 2 for r in returns) / len(returns)
        return math.sqrt(variance) * 100  # as percentage

    @staticmethod
    def calculate_support_resistance(prices: list[float]) -> dict[str, float]:
        if len(prices) < 5:
            p = prices[-1] if prices else 0.0
            return {"support": p * 0.95, "resistance": p * 1.05, "current": p}
        recent = prices[-50:] if len(prices) >= 50 else prices
        support = min(recent)
        resistance = max(recent)
        # Refine: pivot-like approach using local minima/maxima
        lows = sorted(recent)[:max(1, len(recent) // 5)]
        highs = sorted(recent, reverse=True)[:max(1, len(recent) // 5)]
        support = sum(lows) / len(lows)
        resistance = sum(highs) / len(highs)
        return {"support": support, "resistance": resistance, "current": prices[-1]}

    # ------------------------------------------------------------------ scorer

    def score_technical(self, klines: dict) -> dict:
        closes = klines.get("close", [])
        volumes = klines.get("volume", [])

        if len(closes) < 30:
            return _default_tech_score()

        rsi = self.calculate_rsi(closes)
        macd = self.calculate_macd(closes)
        mas = self.calculate_ma(closes)
        emas = self.calculate_ema(closes)
        bb = self.calculate_bollinger(closes)
        vol = self.calculate_volatility(closes)
        sr = self.calculate_support_resistance(closes)

        # RSI score (oversold=bullish 0-30 → high score, overbought=bearish 70-100 → low)
        if rsi < 30:
            rsi_score = 80 + (30 - rsi) * (20 / 30)
        elif rsi > 70:
            rsi_score = 20 - (rsi - 70) * (20 / 30)
        else:
            # 30-70 maps linearly to 35-65
            rsi_score = 35 + (rsi - 30) * (30 / 40)
        rsi_score = max(0.0, min(100.0, rsi_score))

        # MACD score
        if macd["histogram"] > 0 and macd["macd"] > macd["signal"]:
            macd_score = 65.0 + min(35.0, abs(macd["histogram"]) / max(abs(macd["macd"]), 1) * 100)
        elif macd["histogram"] < 0 and macd["macd"] < macd["signal"]:
            macd_score = 35.0 - min(35.0, abs(macd["histogram"]) / max(abs(macd["macd"]), 1) * 100)
        else:
            macd_score = 50.0
        macd_score = max(0.0, min(100.0, macd_score))

        # MA trend score (price vs MA20 and MA50)
        current = closes[-1]
        ma20 = mas.get("ma20", current)
        ma50 = mas.get("ma50", current)
        ma_score = 50.0
        if current > ma20 > ma50:
            ma_score = 75.0
        elif current > ma20:
            ma_score = 65.0
        elif current > ma50:
            ma_score = 55.0
        elif current < ma20 < ma50:
            ma_score = 25.0
        elif current < ma20:
            ma_score = 35.0
        else:
            ma_score = 45.0

        # Bollinger score
        pct_b = bb["pct_b"]
        if pct_b < 0:
            bb_score = 80.0
        elif pct_b > 1:
            bb_score = 20.0
        else:
            bb_score = 80.0 - pct_b * 60.0
        bb_score = max(0.0, min(100.0, bb_score))

        # Volatility score: very high volatility → neutral/bearish; moderate = neutral
        if vol < 1.0:
            vol_score = 60.0
        elif vol < 3.0:
            vol_score = 50.0
        elif vol < 6.0:
            vol_score = 40.0
        else:
            vol_score = 30.0

        # Weighted aggregate
        weights = TECHNICAL_WEIGHTS
        composite = (
            rsi_score * weights["rsi"]
            + macd_score * weights["macd"]
            + ma_score * weights["ma_trend"]
            + bb_score * weights["bollinger"]
            + vol_score * weights["volatility"]
        )

        macd_signal_text = (
            "bullish" if macd["histogram"] > 0 else "bearish" if macd["histogram"] < 0 else "neutral"
        )
        bb_pos = "oversold" if pct_b < 0.2 else "overbought" if pct_b > 0.8 else "middle"
        ma_trend = "uptrend" if current > ma20 > ma50 else "downtrend" if current < ma20 < ma50 else "mixed"

        return {
            "score": round(composite, 2),
            "rsi": round(rsi, 2),
            "rsi_score": round(rsi_score, 2),
            "macd": {k: round(v, 6) for k, v in macd.items()},
            "macd_score": round(macd_score, 2),
            "macd_signal": macd_signal_text,
            "ma": {k: round(v, 2) for k, v in mas.items()},
            "ma_trend": ma_trend,
            "ma_score": round(ma_score, 2),
            "bollinger": {k: round(v, 4) for k, v in bb.items()},
            "bollinger_position": bb_pos,
            "bb_score": round(bb_score, 2),
            "volatility": round(vol, 4),
            "volatility_score": round(vol_score, 2),
            "support_resistance": {k: round(v, 2) for k, v in sr.items()},
        }


def _default_tech_score() -> dict:
    return {
        "score": 50.0,
        "rsi": 50.0,
        "rsi_score": 50.0,
        "macd": {"macd": 0.0, "signal": 0.0, "histogram": 0.0},
        "macd_score": 50.0,
        "macd_signal": "neutral",
        "ma": {},
        "ma_trend": "mixed",
        "ma_score": 50.0,
        "bollinger": {"upper": 0.0, "middle": 0.0, "lower": 0.0, "pct_b": 0.5},
        "bollinger_position": "middle",
        "bb_score": 50.0,
        "volatility": 0.0,
        "volatility_score": 50.0,
        "support_resistance": {"support": 0.0, "resistance": 0.0, "current": 0.0},
    }

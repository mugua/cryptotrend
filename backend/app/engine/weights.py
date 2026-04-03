"""Factor weight constants for the trend scoring engine."""

FACTOR_WEIGHTS: dict[str, float] = {
    "technical": 0.30,
    "onchain": 0.20,
    "sentiment": 0.20,
    "macro": 0.15,
    "market_structure": 0.15,
}

# Sub-factor weights within each factor group
TECHNICAL_WEIGHTS: dict[str, float] = {
    "rsi": 0.25,
    "macd": 0.20,
    "ma_trend": 0.25,
    "bollinger": 0.15,
    "volatility": 0.15,
}

ONCHAIN_WEIGHTS: dict[str, float] = {
    "active_addresses": 0.25,
    "whale_activity": 0.20,
    "exchange_flow": 0.20,
    "hash_rate": 0.20,
    "gas_fee": 0.15,
}

SENTIMENT_WEIGHTS: dict[str, float] = {
    "fear_greed": 0.35,
    "social": 0.20,
    "google_trends": 0.15,
    "funding_rate": 0.15,
    "long_short": 0.15,
}

MACRO_WEIGHTS: dict[str, float] = {
    "dxy": 0.30,
    "treasury_yield": 0.25,
    "vix": 0.25,
    "m2": 0.20,
}

MARKET_STRUCTURE_WEIGHTS: dict[str, float] = {
    "btc_dominance": 0.25,
    "stablecoin": 0.20,
    "open_interest": 0.20,
    "eth_btc_ratio": 0.15,
    "volume": 0.20,
}

SCORE_LEVELS: dict[tuple[int, int], str] = {
    (80, 100): "Strong Bullish",
    (60, 79): "Bullish",
    (40, 59): "Neutral",
    (20, 39): "Bearish",
    (0, 19): "Strong Bearish",
}

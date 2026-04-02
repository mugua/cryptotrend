from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ─── Market Data ─────────────────────────────────────────────────────────────

class CoinPrice(BaseModel):
    coin_id: str
    symbol: str
    name: str
    price_usd: float
    change_24h: float
    market_cap: float
    volume_24h: float
    last_updated: datetime


class MarketOverview(BaseModel):
    total_market_cap: float
    total_volume_24h: float
    btc_dominance: float
    eth_dominance: float
    stablecoin_market_cap: float
    active_coins: int
    last_updated: datetime


class KlineData(BaseModel):
    symbol: str
    interval: str
    open_time: list[int]
    open: list[float]
    high: list[float]
    low: list[float]
    close: list[float]
    volume: list[float]


# ─── Factor Scores ────────────────────────────────────────────────────────────

class FactorScore(BaseModel):
    name: str
    score: float = Field(..., ge=0, le=100)
    weight: float
    weighted_score: float
    signal: str  # bullish / bearish / neutral
    details: dict


class TechnicalFactors(BaseModel):
    rsi: float
    macd_signal: str
    ma_trend: str
    bollinger_position: str
    volatility: float
    score: float
    details: dict


class OnchainFactors(BaseModel):
    active_addresses_score: float
    whale_activity_score: float
    exchange_flow_score: float
    hash_rate_score: float
    gas_fee_score: float
    score: float
    details: dict


class SentimentFactors(BaseModel):
    fear_greed_value: int
    fear_greed_classification: str
    social_score: float
    google_trends_score: float
    funding_rate_score: float
    long_short_score: float
    score: float
    details: dict


class MacroFactors(BaseModel):
    dxy_score: float
    treasury_yield_score: float
    vix_score: float
    m2_score: float
    correlation_spx: float
    score: float
    details: dict


class MarketStructureFactors(BaseModel):
    btc_dominance_score: float
    stablecoin_score: float
    open_interest_score: float
    eth_btc_ratio_score: float
    volume_score: float
    score: float
    details: dict


class FactorSnapshot(BaseModel):
    technical: TechnicalFactors
    onchain: OnchainFactors
    sentiment: SentimentFactors
    macro: MacroFactors
    market_structure: MarketStructureFactors


# ─── Trend Score ──────────────────────────────────────────────────────────────

class TrendScore(BaseModel):
    coin_id: str
    coin_name: str
    overall_score: float = Field(..., ge=0, le=100)
    trend_level: str
    technical_score: float
    onchain_score: float
    sentiment_score: float
    macro_score: float
    market_structure_score: float
    factor_scores: list[FactorScore]
    timestamp: datetime
    summary: str


# ─── Reports ──────────────────────────────────────────────────────────────────

class TrendReportSummary(BaseModel):
    id: str
    coin_id: str
    coin_name: str
    overall_score: float
    trend_level: str
    created_at: datetime


class TrendReport(BaseModel):
    id: str
    coin_id: str
    coin_name: str
    overall_score: float
    trend_level: str
    trend_score: TrendScore
    factor_snapshot: FactorSnapshot
    markdown_report: str
    key_signals: list[str]
    conclusion: str
    created_at: datetime


# ─── API Responses ────────────────────────────────────────────────────────────

class PricesResponse(BaseModel):
    coins: list[CoinPrice]
    last_updated: datetime


class AnalysisResponse(BaseModel):
    coin_id: str
    trend_score: TrendScore
    factors: Optional[FactorSnapshot] = None

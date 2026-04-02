# Factor System Documentation

## Overview

CryptoTrend uses a **5-dimension factor scoring system** to evaluate cryptocurrency trends. Each dimension contains multiple sub-factors that are individually scored (0-100) and then combined into a weighted overall score.

## Dimension Weights

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Technical Analysis | 30% | Most directly reflects price action and momentum |
| On-chain Data | 20% | Fundamental blockchain activity metrics |
| Market Sentiment | 20% | Crowd psychology and derivatives positioning |
| Macro Economics | 15% | External economic forces affecting crypto |
| Market Structure | 15% | Internal market dynamics and capital flows |

---

## 1. Technical Analysis (30%)

### Moving Averages (MA)
- **Periods**: 5, 10, 20, 50, 200 days
- **Formula**: MA(n) = Σ(Close_i) / n for i = 1 to n
- **Signal**: Price above MA = Bullish, Price below MA = Bearish
- **Golden Cross**: Short MA crosses above Long MA (Bullish)
- **Death Cross**: Short MA crosses below Long MA (Bearish)

### Exponential Moving Average (EMA)
- **Periods**: 12, 26 days
- **Formula**: EMA_t = Price_t × k + EMA_(t-1) × (1 - k), where k = 2/(n+1)
- **Usage**: Faster response to recent price changes than SMA

### RSI (Relative Strength Index)
- **Period**: 14 days
- **Formula**: RSI = 100 - (100 / (1 + RS)), where RS = Avg Gain / Avg Loss
- **Scoring**: RSI < 30 = Oversold (Bullish), RSI > 70 = Overbought (Bearish), 30-70 = Neutral

### MACD (Moving Average Convergence Divergence)
- **Components**: MACD Line (EMA12 - EMA26), Signal Line (EMA9 of MACD), Histogram
- **Bullish**: MACD crosses above Signal, Histogram turns positive
- **Bearish**: MACD crosses below Signal, Histogram turns negative

### Bollinger Bands
- **Period**: 20 days, 2 standard deviations
- **Upper Band**: MA20 + 2σ
- **Lower Band**: MA20 - 2σ
- **Signal**: Price near lower band = potential bounce, near upper = potential reversal

### Volatility
- **Period**: 30-day rolling standard deviation of daily returns
- **High volatility**: Indicates uncertainty (slightly bearish for trend)
- **Low volatility**: Often precedes a breakout

---

## 2. On-chain Data (20%)

### Active Addresses
- **Source**: Blockchain.com (BTC), Etherscan (ETH)
- **Signal**: Rising = growing network usage (Bullish), Declining = less activity (Bearish)

### Whale Transactions
- **Source**: Whale Alert API
- **Signal**: Large exchange deposits = potential selling (Bearish), Large withdrawals = accumulation (Bullish)

### Exchange Net Flow
- **Signal**: Net inflow to exchanges = selling pressure (Bearish), Net outflow = accumulation (Bullish)

### Hash Rate (BTC) / Gas Fee (ETH)
- **BTC**: Rising hash rate = miners bullish on future price
- **ETH**: Rising gas = network demand increasing

### MVRV Ratio (Market Value to Realized Value)
- **Formula**: MVRV = Market Cap / Realized Cap
- **Scoring**: MVRV > 3.5 = Overvalued (Bearish), MVRV < 1 = Undervalued (Bullish)

### NVT Ratio (Network Value to Transactions)
- **Formula**: NVT = Market Cap / Daily Transaction Volume
- **Scoring**: High NVT = overvalued relative to usage, Low NVT = undervalued

---

## 3. Market Sentiment (20%)

### Fear & Greed Index
- **Source**: Alternative.me
- **Range**: 0 (Extreme Fear) to 100 (Extreme Greed)
- **Contrarian Signal**: Extreme Fear → Bullish, Extreme Greed → Bearish

### Social Sentiment (Reddit)
- **Source**: Reddit API (r/bitcoin, r/ethereum)
- **Metrics**: Subscriber growth, active users, post engagement

### Google Trends
- **Source**: pytrends library
- **Signal**: Sudden spike = retail FOMO (often late-stage Bullish/early Bearish)

### Funding Rate
- **Source**: Binance Futures
- **Signal**: High positive = overcrowded longs (Bearish contrarian), Negative = potential short squeeze (Bullish)

### Long/Short Ratio
- **Source**: Binance
- **Signal**: Extreme long ratio = Bearish contrarian, Extreme short = Bullish contrarian

---

## 4. Macro Economics (15%)

### DXY (US Dollar Index)
- **Correlation**: Generally inverse to BTC
- **Signal**: Rising DXY = headwind for crypto (Bearish), Falling DXY = tailwind (Bullish)

### 10-Year Treasury Yield
- **Signal**: Rising yields = risk-off (Bearish for crypto), Falling = risk-on (Bullish)

### VIX (Volatility Index)
- **Signal**: High VIX = market fear, mixed for crypto; Very high VIX = potential bounce

### SPX Correlation
- **Note**: BTC increasingly correlates with stocks
- **Signal**: High correlation means macro events affect crypto more directly

### M2 Money Supply
- **Signal**: Expanding M2 = more liquidity, historically Bullish for crypto

---

## 5. Market Structure (15%)

### BTC Dominance
- **Signal**: Rising dominance = flight to quality (alt-bearish), Falling = alt-season (risk-on)

### Stablecoin Supply
- **Signal**: Growing stablecoin supply = dry powder on sidelines (Bullish), Declining = capital leaving

### Open Interest (Futures)
- **Signal**: Rising OI with rising price = strong trend, Rising OI with falling price = potential long squeeze

### ETH/BTC Ratio
- **Signal**: Rising ETH/BTC = risk appetite (Bullish sentiment), Falling = risk-off

### Volume Change
- **Signal**: Rising volume confirms trend, Declining volume = weakening trend

---

## Score Interpretation

| Score | Level | Description |
|-------|-------|-------------|
| 80-100 | Strong Bullish 🟢 | Multiple strong bullish signals across dimensions |
| 60-79 | Bullish 🟢 | More bullish than bearish signals |
| 40-59 | Neutral 🟡 | Mixed signals, no clear direction |
| 20-39 | Bearish 🔴 | More bearish than bullish signals |
| 0-19 | Strong Bearish 🔴 | Multiple strong bearish signals across dimensions |

---

## Data Sources

| Source | API | Free Tier |
|--------|-----|-----------|
| CoinGecko | REST | 10-30 req/min |
| Binance | REST | 1200 req/min |
| Blockchain.com | REST | Generous |
| Etherscan | REST | 5 req/sec (with key) |
| Alternative.me | REST | Unlimited |
| FRED | REST | 120 req/min |
| Reddit | REST | 60 req/min |
| Google Trends | pytrends | Rate limited |
| Yahoo Finance | yfinance | Rate limited |
| Whale Alert | REST | 10 req/min (free) |

# API Documentation

## Backend API (FastAPI — Port 8000)

Base URL: `http://localhost:8000`

---

### Market Data

#### GET `/api/market/prices`
Returns current prices for top cryptocurrencies.

**Response:**
```json
[
  {
    "id": "bitcoin",
    "symbol": "btc",
    "name": "Bitcoin",
    "price": 67500.00,
    "change24h": 2.35,
    "marketCap": 1325000000000,
    "volume24h": 28500000000,
    "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
  }
]
```

#### GET `/api/market/kline/{symbol}`
Returns K-line (candlestick) data.

**Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| symbol | path | required | Trading pair (e.g., BTCUSDT) |
| interval | query | 1d | Candle interval (1m/5m/1h/4h/1d/1w) |
| limit | query | 100 | Number of candles |

**Response:**
```json
[
  {
    "time": "2024-01-15",
    "open": 67000,
    "high": 68500,
    "low": 66800,
    "close": 68200,
    "volume": 25000
  }
]
```

#### GET `/api/market/overview`
Returns market overview data.

**Response:**
```json
{
  "totalMarketCap": 2650000000000,
  "total24hVolume": 85000000000,
  "btcDominance": 52.3,
  "fearGreedIndex": 65,
  "fearGreedLabel": "Greed",
  "topGainers": [],
  "topLosers": []
}
```

---

### Analysis

#### GET `/api/analysis/trend-score/{coin_id}`
Returns the comprehensive trend score for a coin.

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| coin_id | path | Coin ID (e.g., bitcoin, ethereum) |

**Response:**
```json
{
  "coinId": "bitcoin",
  "overallScore": 68.5,
  "trendLevel": "Bullish",
  "technicalScore": 72.0,
  "onchainScore": 65.0,
  "sentimentScore": 70.0,
  "macroScore": 55.0,
  "structureScore": 68.0,
  "signal": "Moderate uptrend expected",
  "confidence": 0.75,
  "timestamp": "2024-01-15T12:00:00Z"
}
```

#### GET `/api/analysis/factors/{coin_id}`
Returns detailed factor data for all 5 dimensions.

**Response:**
```json
{
  "technical": {
    "ma": {"5": {"value": 67500, "signal": "bullish"}, ...},
    "rsi": {"value": 62.5, "signal": "neutral"},
    "macd": {"macd": 150.5, "signal": 120.3, "histogram": 30.2, "trend": "bullish"},
    "bollinger": {"upper": 70000, "middle": 67000, "lower": 64000, "position": "middle"},
    "volatility": {"value": 0.035, "percentile": 45},
    "score": 72.0
  },
  "onchain": { ... },
  "sentiment": { ... },
  "macro": { ... },
  "marketStructure": { ... }
}
```

#### GET `/api/analysis/technical/{coin_id}`
Returns technical analysis factors only.

#### GET `/api/analysis/onchain/{coin_id}`
Returns on-chain analysis factors only.

#### GET `/api/analysis/sentiment/{coin_id}`
Returns sentiment analysis factors only.

#### GET `/api/analysis/macro`
Returns macro economic factors.

#### GET `/api/analysis/market-structure`
Returns market structure factors.

---

### Reports

#### GET `/api/reports`
Returns list of generated trend reports.

**Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| coin_id | query | all | Filter by coin |
| limit | query | 20 | Number of reports |
| offset | query | 0 | Pagination offset |

**Response:**
```json
[
  {
    "id": "rpt_abc123",
    "coinId": "bitcoin",
    "coinName": "Bitcoin",
    "overallScore": 68.5,
    "trendLevel": "Bullish",
    "summary": "BTC shows moderate bullish momentum...",
    "createdAt": "2024-01-15T00:00:00Z"
  }
]
```

#### GET `/api/reports/{id}`
Returns a single report with full details.

#### POST `/api/reports/generate/{coin_id}`
Manually triggers report generation for a coin.

---

## Frontend BFF Routes (Next.js — Port 3000)

These routes proxy to the backend with fallback mock data.

| Method | Path | Backend Proxy | Description |
|--------|------|---------------|-------------|
| GET | `/api/market/prices` | `/api/market/prices` | Coin prices |
| GET | `/api/market/kline` | `/api/market/kline/{symbol}` | K-line data |
| GET | `/api/market/overview` | `/api/market/overview` | Market overview |
| GET | `/api/analysis/trend-score` | `/api/analysis/trend-score/{coin_id}` | Trend score |
| GET | `/api/analysis/factors` | `/api/analysis/factors/{coin_id}` | All factors |
| GET | `/api/reports` | `/api/reports` | Report list |
| POST | `/api/reports` | `/api/reports/generate/{coin_id}` | Generate report |

---

## Authentication

### POST `/api/auth/register`
Register a new user.

**Body:**
```json
{
  "email": "user@example.com",
  "name": "User Name",
  "password": "securepassword"
}
```

### POST `/api/auth/callback/credentials`
Login with credentials (handled by NextAuth.js).

### GET `/api/auth/session`
Get current session (handled by NextAuth.js).

---

## Error Handling

All endpoints return errors in this format:
```json
{
  "error": "Error description",
  "detail": "Detailed error message (optional)"
}
```

**HTTP Status Codes:**
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 409 | Conflict (e.g., duplicate email) |
| 429 | Rate Limited |
| 500 | Internal Server Error |

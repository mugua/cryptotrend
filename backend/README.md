# CryptoTrend Backend

FastAPI backend for cryptocurrency trend analysis.

## Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /health` — health check
- `GET /api/market/prices` — coin prices
- `GET /api/market/kline/{symbol}` — OHLCV data
- `GET /api/market/overview` — global market overview
- `GET /api/analysis/trend-score/{coin_id}` — trend score (0-100)
- `GET /api/analysis/factors/{coin_id}` — all factor details
- `GET /api/analysis/technical/{coin_id}` — technical indicators
- `GET /api/analysis/onchain/{coin_id}` — on-chain metrics
- `GET /api/analysis/sentiment/{coin_id}` — sentiment data
- `GET /api/analysis/macro` — macro economic factors
- `GET /api/analysis/market-structure` — market structure
- `GET /api/reports/` — list reports
- `GET /api/reports/{id}` — get report
- `POST /api/reports/generate/{coin_id}` — trigger report generation

## Supported Coins

bitcoin, ethereum, binancecoin, solana, xrp, cardano, avalanche-2, polkadot, chainlink, litecoin

## Environment Variables (`.env`)

```
ETHERSCAN_API_KEY=
FRED_API_KEY=
WHALE_ALERT_API_KEY=
DATABASE_URL=sqlite+aiosqlite:///./cryptotrend.db
REDIS_URL=redis://localhost:6379/0
```

## Docker

```bash
docker build -t cryptotrend-backend .
docker run -p 8000:8000 cryptotrend-backend
```

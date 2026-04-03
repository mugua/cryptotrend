# 🚀 CryptoTrend — Cryptocurrency Trend Analysis System

[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A comprehensive BTC/ETH cryptocurrency trend analysis system with multi-dimensional factor scoring, automated report generation, dark/light themes, and i18n support (EN/ZH/JA/KO).

---

## ✨ Features

- 📊 **Real-time Dashboard** — Live prices, market cap, 24h volume, Fear & Greed Index for top 10 coins
- 📈 **TradingView Charts** — Interactive candlestick charts powered by lightweight-charts
- 🔬 **5-Dimension Trend Analysis** — Technical, On-chain, Sentiment, Macro, Market Structure factors
- 🎯 **Trend Scoring Engine** — Weighted 0-100 score with Strong Bullish → Strong Bearish levels
- 📝 **Auto-generated Reports** — Daily trend reports for BTC and ETH
- 🌍 **Internationalization** — English, 中文, 日本語, 한국어
- 🌓 **Dark/Light/System Theme** — Adaptive UI with smooth transitions
- 👤 **User Center** — Auth, profile, settings, watchlist
- 🐳 **Docker Compose** — One-click deployment

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), React 18, TypeScript |
| UI | Tailwind CSS, shadcn/ui, Radix UI |
| Charts | lightweight-charts (TradingView), Recharts |
| State | Zustand, TanStack Query |
| i18n | next-intl (EN/ZH/JA/KO) |
| Theme | next-themes + Tailwind dark mode |
| Auth | NextAuth.js (JWT + Credentials) |
| Database | Prisma ORM, SQLite (dev) / PostgreSQL (prod) |
| Backend | Python FastAPI, pandas, numpy |
| Scheduler | APScheduler |
| Deploy | Docker Compose |

---

## 🚀 Quick Start

### Docker Compose (Recommended)

```bash
git clone https://github.com/mugua/cryptotrend.git
cd cryptotrend
cp .env.example .env
docker compose up -d
```

Open [http://localhost:3000](http://localhost:3000) 🎉

### Manual Development

**Frontend:**
```bash
cd frontend
cp ../.env.example .env.local
npm install
npx prisma generate
npx prisma db push
npm run dev
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## 📁 Project Structure

```
cryptotrend/
├── frontend/                   # Next.js 14 Frontend + BFF
│   ├── app/
│   │   ├── [locale]/           # i18n pages (dashboard, analysis, reports, user, auth)
│   │   └── api/                # BFF Route Handlers
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components (15)
│   │   ├── layout/             # Header, Sidebar, Footer, ThemeToggle
│   │   ├── charts/             # TradingView, Gauge, Radar, LineChart, BarChart, Heatmap
│   │   ├── dashboard/          # MarketOverview, CoinPriceCard, TrendSummary, FearGreed
│   │   ├── analysis/           # 5 factor panels (Technical, OnChain, Sentiment, Macro, Structure)
│   │   └── user/               # LoginForm, RegisterForm, UserAvatar
│   ├── messages/               # i18n translations (en, zh, ja, ko)
│   ├── stores/                 # Zustand stores
│   ├── prisma/                 # Database schema
│   └── lib/                    # Utilities, auth, prisma client
│
├── backend/                    # Python FastAPI Trend Engine
│   └── app/
│       ├── collectors/         # 10 data collectors (CoinGecko, Binance, FRED, etc.)
│       ├── engine/             # 5 analyzers + scorer + weights
│       ├── reports/            # Report generator + templates
│       ├── scheduler/          # APScheduler jobs
│       └── api/                # REST API routes
│
├── docs/                       # Documentation
├── docker-compose.yml          # One-click deployment
└── .env.example                # Environment variables
```

---

## 📊 Trend Scoring System

### 5 Dimensions

| Dimension | Weight | Key Factors |
|-----------|--------|-------------|
| 🔧 Technical | 30% | MA, EMA, RSI, MACD, Bollinger Bands, Volatility |
| ⛓ On-chain | 20% | Active Addresses, Whale Txs, Exchange Flow, Hash Rate, MVRV, NVT |
| 💭 Sentiment | 20% | Fear & Greed, Reddit, Google Trends, Funding Rate, Long/Short Ratio |
| 🌐 Macro | 15% | DXY, 10Y Yield, VIX, SPX Correlation, M2 Supply |
| 🏗 Market Structure | 15% | BTC Dominance, Stablecoin Supply, Open Interest, ETH/BTC, Volume |

### Score Interpretation

| Score Range | Level | Signal |
|-------------|-------|--------|
| 80–100 | 🟢 Strong Bullish | Strong uptrend expected |
| 60–79 | 🟢 Bullish | Moderate uptrend expected |
| 40–59 | 🟡 Neutral | No clear direction |
| 20–39 | 🔴 Bearish | Moderate downtrend expected |
| 0–19 | 🔴 Strong Bearish | Strong downtrend expected |

---

## 🔌 Free Data Sources

| Source | Data | Rate Limit |
|--------|------|-----------|
| CoinGecko | Prices, Market Cap, Volume, Dominance | 10-30 req/min |
| Binance | K-lines, Funding Rate, Open Interest | 1200 req/min |
| Blockchain.com | BTC Active Addresses, Hash Rate | Generous |
| Etherscan | ETH Gas, Supply, Tx Count | 5 req/sec |
| Alternative.me | Fear & Greed Index | Unlimited |
| FRED | DXY, Treasury Yield, M2, CPI | 120 req/min |
| Reddit | Subreddit Stats | 60 req/min |
| Google Trends | Search Interest | Via pytrends |
| Yahoo Finance | SPX, VIX, Gold | Via yfinance |

---

## 🔧 Environment Variables

See [`.env.example`](.env.example) for all available configuration options.

---

## 📖 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Factor System](docs/FACTORS.md)
- [API Reference](docs/API.md)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">Built with ❤️ for crypto traders and analysts</p>

# Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                        Client (Browser)                       │
│     Next.js 14 App Router + React 18 + Tailwind + shadcn/ui │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌─────────────────┐  │
│  │Dashboard │ │Analysis  │ │Reports  │ │User Center      │  │
│  │  Page    │ │  Pages   │ │  Pages  │ │(Profile/Settings)│  │
│  └────┬─────┘ └────┬─────┘ └────┬────┘ └──────┬──────────┘  │
│       └─────────────┴────────────┴─────────────┘             │
│                          │                                    │
│              TanStack Query (30s polling)                     │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTP (fetch)
┌──────────────────────────▼───────────────────────────────────┐
│                    BFF API Routes (Next.js)                   │
│         /api/market/*  /api/analysis/*  /api/reports/*        │
│         /api/auth/*    (NextAuth.js + Prisma)                │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTP (proxy)
┌──────────────────────────▼───────────────────────────────────┐
│               Backend (Python FastAPI :8000)                  │
│  ┌────────────┐ ┌──────────────┐ ┌─────────────────────────┐│
│  │Collectors  │ │Engine        │ │Reports                  ││
│  │(10 sources)│→│(5 analyzers) │→│(generator + templates)  ││
│  └────────────┘ └──────────────┘ └─────────────────────────┘│
│  ┌────────────┐ ┌──────────────┐                             │
│  │Scheduler   │ │API Routes    │                             │
│  │(APScheduler│ │(market/      │                             │
│  │ cron jobs) │ │ analysis/    │                             │
│  └────────────┘ │ reports)     │                             │
│                 └──────────────┘                             │
└──────────────────────────┬───────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
  ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
  │ PostgreSQL   │ │ Redis       │ │ External APIs│
  │ (Users,      │ │ (Cache)     │ │ (CoinGecko,  │
  │  Reports,    │ │             │ │  Binance,    │
  │  MarketData) │ │             │ │  FRED, etc.) │
  └──────────────┘ └─────────────┘ └──────────────┘
```

## Frontend Architecture

### Next.js App Router

- **`app/[locale]/`** — Internationalized routes with `next-intl`
- **`app/api/`** — BFF (Backend For Frontend) route handlers
- **Server Components** — Layout, static pages
- **Client Components** — Interactive pages, charts, forms

### Component Hierarchy

```
Layout (Server)
├── Providers (Client: Theme + Query + Session)
│   ├── Header (Client: nav, search, theme toggle, language switcher)
│   ├── Sidebar (Client: collapsible navigation)
│   ├── Main Content Area
│   │   └── Page Components (Client)
│   └── Footer (Server)
```

### Data Flow

1. **TanStack Query** polls BFF routes every 30 seconds
2. **BFF routes** proxy to Python backend (with 5s timeout + mock fallback)
3. **Zustand stores** hold client-side UI state (selected coin, theme, locale)
4. **NextAuth.js** manages JWT sessions

## Backend Architecture

### Data Collection Pipeline

```
Scheduler (APScheduler)
  │
  ├── Every 5 min:  Price data (CoinGecko, Binance)
  ├── Every 1 hour: On-chain + Sentiment data
  ├── Every 6 hours: Macro economic data
  └── Every 24 hours: Generate trend reports
  │
  ▼
Collectors (10 sources) → Raw Data → Engine (5 analyzers) → Scorer → Reports
```

### Scoring Pipeline

```
Raw Data → Factor Analyzers → Factor Scores (0-100) → Weighted Average → Overall Score
                                                         │
                                                         ▼
                                                   Trend Level Classification
                                                   (Strong Bullish → Strong Bearish)
```

## Database Schema

- **User** — Authentication, preferences (locale, theme)
- **Watchlist** — User's watched coins (unique per user+coin)
- **TrendReport** — Generated reports with all scores and analysis
- **MarketData** — Historical price/volume snapshots
- **FactorSnapshot** — Individual factor scores over time

## Deployment

Docker Compose orchestrates 4 services:
- `frontend` (Node.js, port 3000)
- `backend` (Python, port 8000)
- `postgres` (port 5432)
- `redis` (port 6379)

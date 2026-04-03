import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const MOCK_OVERVIEW = {
  total_market_cap: 2450000000000,
  total_volume_24h: 98000000000,
  btc_dominance: 52.4,
  eth_dominance: 17.1,
  active_cryptocurrencies: 12345,
  market_cap_change_24h: 1.87,
  top_gainers: [
    { symbol: 'SOLUSDT', name: 'Solana', change_24h: 5.67 },
    { symbol: 'AVAXUSDT', name: 'Avalanche', change_24h: 4.12 },
    { symbol: 'DOGEUSDT', name: 'Dogecoin', change_24h: 3.45 },
  ],
  top_losers: [
    { symbol: 'DOTUSDT', name: 'Polkadot', change_24h: -2.10 },
    { symbol: 'XRPUSDT', name: 'XRP', change_24h: -1.23 },
    { symbol: 'BNBUSDT', name: 'BNB', change_24h: -0.89 },
  ],
  fear_greed_index: 65,
  fear_greed_label: 'Greed',
};

export async function GET(request: NextRequest) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/market/overview`, {
      next: { revalidate: 30 },
      signal: AbortSignal.timeout(5000),
    });
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (e) {
    // Backend unavailable, fall through to mock data
  }
  return NextResponse.json(MOCK_OVERVIEW);
}

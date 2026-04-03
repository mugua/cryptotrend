import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const MOCK_PRICES = [
  { symbol: 'BTCUSDT', name: 'Bitcoin', price: 67234.50, change_24h: 2.34, volume_24h: 28500000000, market_cap: 1320000000000 },
  { symbol: 'ETHUSDT', name: 'Ethereum', price: 3456.78, change_24h: 1.56, volume_24h: 15200000000, market_cap: 415000000000 },
  { symbol: 'BNBUSDT', name: 'BNB', price: 584.32, change_24h: -0.89, volume_24h: 1800000000, market_cap: 89000000000 },
  { symbol: 'SOLUSDT', name: 'Solana', price: 172.45, change_24h: 5.67, volume_24h: 3200000000, market_cap: 76000000000 },
  { symbol: 'XRPUSDT', name: 'XRP', price: 0.5234, change_24h: -1.23, volume_24h: 1200000000, market_cap: 28000000000 },
  { symbol: 'ADAUSDT', name: 'Cardano', price: 0.4567, change_24h: 0.78, volume_24h: 450000000, market_cap: 16000000000 },
  { symbol: 'DOGEUSDT', name: 'Dogecoin', price: 0.1234, change_24h: 3.45, volume_24h: 890000000, market_cap: 17500000000 },
  { symbol: 'DOTUSDT', name: 'Polkadot', price: 7.89, change_24h: -2.10, volume_24h: 320000000, market_cap: 10500000000 },
  { symbol: 'MATICUSDT', name: 'Polygon', price: 0.7823, change_24h: 1.90, volume_24h: 410000000, market_cap: 7200000000 },
  { symbol: 'AVAXUSDT', name: 'Avalanche', price: 35.67, change_24h: 4.12, volume_24h: 560000000, market_cap: 13200000000 },
];

export async function GET(request: NextRequest) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/market/prices`, {
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
  return NextResponse.json(MOCK_PRICES);
}

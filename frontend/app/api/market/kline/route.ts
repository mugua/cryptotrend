import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

function generateMockKline(limit: number) {
  const now = Date.now();
  const interval = 86400000; // 1 day in ms
  let basePrice = 67000;
  const data = [];

  for (let i = limit - 1; i >= 0; i--) {
    const time = now - i * interval;
    const open = basePrice + (Math.random() - 0.5) * 2000;
    const close = open + (Math.random() - 0.5) * 1500;
    const high = Math.max(open, close) + Math.random() * 800;
    const low = Math.min(open, close) - Math.random() * 800;
    const volume = 15000 + Math.random() * 30000;
    data.push({
      time: Math.floor(time / 1000),
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume: parseFloat(volume.toFixed(2)),
    });
    basePrice = close;
  }
  return data;
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const symbol = searchParams.get('symbol') || 'BTCUSDT';
  const interval = searchParams.get('interval') || '1d';
  const limit = parseInt(searchParams.get('limit') || '100', 10);

  try {
    const res = await fetch(
      `${BACKEND_URL}/api/market/kline/${symbol}?interval=${interval}&limit=${limit}`,
      { next: { revalidate: 30 }, signal: AbortSignal.timeout(5000) }
    );
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (e) {
    // Backend unavailable, fall through to mock data
  }
  return NextResponse.json(generateMockKline(limit));
}

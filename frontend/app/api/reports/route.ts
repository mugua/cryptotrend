import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const MOCK_REPORTS = [
  {
    id: 'rpt-001',
    coin_id: 'bitcoin',
    symbol: 'BTC',
    title: 'Bitcoin Trend Analysis Report',
    summary: 'Bitcoin shows strong bullish momentum with key support at $65,000. Technical indicators suggest continued uptrend with a target of $72,000.',
    trend_score: 72,
    signal: 'bullish',
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 'rpt-002',
    coin_id: 'ethereum',
    symbol: 'ETH',
    title: 'Ethereum Trend Analysis Report',
    summary: 'Ethereum maintaining strength above $3,400 support. DeFi activity increasing with positive on-chain metrics.',
    trend_score: 68,
    signal: 'bullish',
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 'rpt-003',
    coin_id: 'solana',
    symbol: 'SOL',
    title: 'Solana Trend Analysis Report',
    summary: 'Solana experiencing strong momentum with growing ecosystem adoption. Network performance metrics remain robust.',
    trend_score: 75,
    signal: 'bullish',
    created_at: new Date(Date.now() - 172800000).toISOString(),
  },
];

export async function GET(request: NextRequest) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/reports`, {
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
  return NextResponse.json(MOCK_REPORTS);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const coinId = body.coin_id;
    if (!coinId) {
      return NextResponse.json({ error: 'coin_id is required' }, { status: 400 });
    }

    try {
      const res = await fetch(`${BACKEND_URL}/api/reports/generate/${coinId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(15000),
      });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data, { status: 201 });
      }
    } catch (e) {
      // Backend unavailable, fall through to mock response
    }

    return NextResponse.json(
      {
        id: `rpt-${Date.now()}`,
        coin_id: coinId,
        symbol: coinId.toUpperCase().slice(0, 4),
        title: `${coinId.charAt(0).toUpperCase() + coinId.slice(1)} Trend Analysis Report`,
        summary: `Generated trend analysis report for ${coinId}. The asset shows mixed signals with moderate momentum.`,
        trend_score: 65,
        signal: 'neutral',
        created_at: new Date().toISOString(),
      },
      { status: 201 }
    );
  } catch (error) {
    return NextResponse.json({ error: 'Failed to generate report' }, { status: 500 });
  }
}

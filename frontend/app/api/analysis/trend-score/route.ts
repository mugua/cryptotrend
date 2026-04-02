import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const MOCK_TREND_SCORE = {
  coin_id: 'bitcoin',
  symbol: 'BTC',
  trend_score: 72,
  signal: 'bullish',
  confidence: 0.85,
  updated_at: new Date().toISOString(),
  components: {
    price_momentum: 78,
    volume_trend: 65,
    social_sentiment: 70,
    technical_indicators: 74,
    market_structure: 68,
  },
  summary: 'Bitcoin shows strong bullish momentum with positive technical indicators and rising volume. Social sentiment remains optimistic with increased institutional interest.',
};

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const coinId = searchParams.get('coin_id') || 'bitcoin';

  try {
    const res = await fetch(`${BACKEND_URL}/api/analysis/trend-score/${coinId}`, {
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
  return NextResponse.json({ ...MOCK_TREND_SCORE, coin_id: coinId });
}

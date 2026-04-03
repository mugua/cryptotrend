import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const MOCK_FACTORS = {
  coin_id: 'bitcoin',
  symbol: 'BTC',
  updated_at: new Date().toISOString(),
  factors: {
    technical: {
      score: 74,
      weight: 0.25,
      indicators: [
        { name: 'RSI (14)', value: 62.5, signal: 'bullish', description: 'RSI indicates moderate bullish momentum' },
        { name: 'MACD', value: 1250.3, signal: 'bullish', description: 'MACD line above signal line' },
        { name: 'Moving Average (50)', value: 64500, signal: 'bullish', description: 'Price above 50-day MA' },
        { name: 'Bollinger Bands', value: 0.72, signal: 'neutral', description: 'Price in upper band region' },
      ],
    },
    sentiment: {
      score: 70,
      weight: 0.20,
      indicators: [
        { name: 'Social Media Volume', value: 85000, signal: 'bullish', description: 'High social media activity' },
        { name: 'News Sentiment', value: 0.65, signal: 'bullish', description: 'Predominantly positive news coverage' },
        { name: 'Fear & Greed Index', value: 65, signal: 'neutral', description: 'Market sentiment in greed territory' },
      ],
    },
    on_chain: {
      score: 68,
      weight: 0.20,
      indicators: [
        { name: 'Active Addresses', value: 950000, signal: 'bullish', description: 'Growing network activity' },
        { name: 'Exchange Outflows', value: 12500, signal: 'bullish', description: 'BTC leaving exchanges' },
        { name: 'Hash Rate', value: 580000000, signal: 'bullish', description: 'All-time high hash rate' },
      ],
    },
    market_structure: {
      score: 65,
      weight: 0.20,
      indicators: [
        { name: 'Volume Profile', value: 28500000000, signal: 'bullish', description: 'Above average trading volume' },
        { name: 'Order Book Depth', value: 0.62, signal: 'neutral', description: 'Moderate buy-side depth' },
        { name: 'Funding Rate', value: 0.012, signal: 'neutral', description: 'Slightly positive funding' },
      ],
    },
    macro: {
      score: 60,
      weight: 0.15,
      indicators: [
        { name: 'DXY Correlation', value: -0.45, signal: 'neutral', description: 'Moderate inverse correlation with dollar' },
        { name: 'S&P 500 Correlation', value: 0.35, signal: 'neutral', description: 'Low positive correlation with equities' },
        { name: 'Interest Rate Outlook', value: 0, signal: 'bullish', description: 'Expected rate cuts supportive' },
      ],
    },
  },
};

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const coinId = searchParams.get('coin_id') || 'bitcoin';

  try {
    const res = await fetch(`${BACKEND_URL}/api/analysis/factors/${coinId}`, {
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
  return NextResponse.json({ ...MOCK_FACTORS, coin_id: coinId });
}

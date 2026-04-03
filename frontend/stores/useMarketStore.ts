import { create } from 'zustand';

interface CoinPrice {
  id: string;
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  marketCap: number;
  volume24h: number;
  sparkline?: number[];
  image?: string;
}

interface MarketOverview {
  totalMarketCap: number;
  total24hVolume: number;
  btcDominance: number;
  fearGreedIndex: number;
  fearGreedLabel: string;
}

interface MarketState {
  prices: CoinPrice[];
  overview: MarketOverview | null;
  selectedCoin: string;
  loading: boolean;
  setPrices: (prices: CoinPrice[]) => void;
  setOverview: (overview: MarketOverview) => void;
  setSelectedCoin: (coin: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useMarketStore = create<MarketState>((set) => ({
  prices: [],
  overview: null,
  selectedCoin: 'bitcoin',
  loading: false,
  setPrices: (prices) => set({ prices }),
  setOverview: (overview) => set({ overview }),
  setSelectedCoin: (coin) => set({ selectedCoin: coin }),
  setLoading: (loading) => set({ loading }),
}));

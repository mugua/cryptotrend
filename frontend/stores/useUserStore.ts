import { create } from 'zustand';

interface UserState {
  locale: string;
  theme: string;
  watchlist: string[];
  setLocale: (locale: string) => void;
  setTheme: (theme: string) => void;
  setWatchlist: (watchlist: string[]) => void;
  addToWatchlist: (coinId: string) => void;
  removeFromWatchlist: (coinId: string) => void;
}

export const useUserStore = create<UserState>((set) => ({
  locale: 'en',
  theme: 'system',
  watchlist: [],
  setLocale: (locale) => set({ locale }),
  setTheme: (theme) => set({ theme }),
  setWatchlist: (watchlist) => set({ watchlist }),
  addToWatchlist: (coinId) => set((state) => ({ watchlist: [...state.watchlist, coinId] })),
  removeFromWatchlist: (coinId) => set((state) => ({ watchlist: state.watchlist.filter((id) => id !== coinId) })),
}));

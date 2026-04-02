import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: value < 1 ? 6 : 2,
  }).format(value);
}

export function formatNumber(value: number): string {
  if (value >= 1e12) return `${(value / 1e12).toFixed(2)}T`;
  if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
  if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
  return value.toFixed(2);
}

export function formatPercentage(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
}

export function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600 dark:text-green-400';
  if (score >= 60) return 'text-green-500 dark:text-green-400';
  if (score >= 40) return 'text-yellow-500 dark:text-yellow-400';
  if (score >= 20) return 'text-orange-500 dark:text-orange-400';
  return 'text-red-500 dark:text-red-400';
}

export function getScoreGradient(score: number): string {
  if (score >= 80) return 'from-green-500 to-green-600';
  if (score >= 60) return 'from-green-400 to-green-500';
  if (score >= 40) return 'from-yellow-400 to-yellow-500';
  if (score >= 20) return 'from-orange-400 to-orange-500';
  return 'from-red-500 to-red-600';
}

export const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

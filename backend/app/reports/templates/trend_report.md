# Trend Report Template
# =====================
# {coin_name} Trend Analysis Report
# Generated: {generated_at}

## Executive Summary

**Coin:** {coin_name} ({coin_id})
**Current Price:** ${current_price:,.2f}
**24h Change:** {price_change_24h:+.2f}%
**Report Date:** {generated_at}

{executive_summary}

---

## Overall Trend Score

```
Score: {overall_score}/100  |  Level: {trend_level}
```

| Factor             | Score   | Weight | Weighted | Signal   |
|--------------------|---------|--------|----------|----------|
| Technical Analysis | {tech_score:.1f} | 30%  | {tech_weighted:.1f} | {tech_signal} |
| On-Chain Analysis  | {onchain_score:.1f} | 20% | {onchain_weighted:.1f} | {onchain_signal} |
| Sentiment          | {sentiment_score:.1f} | 20% | {sentiment_weighted:.1f} | {sentiment_signal} |
| Macro Economic     | {macro_score:.1f} | 15%  | {macro_weighted:.1f} | {macro_signal} |
| Market Structure   | {ms_score:.1f} | 15%   | {ms_weighted:.1f} | {ms_signal} |
| **OVERALL**        | **{overall_score:.1f}** | 100% | **{overall_score:.1f}** | **{trend_level}** |

---

## Technical Analysis

**Score: {tech_score:.1f}/100**

| Indicator | Value | Signal |
|-----------|-------|--------|
| RSI (14) | {rsi:.2f} | {rsi_signal} |
| MACD | {macd_histogram:+.6f} | {macd_signal} |
| MA Trend | {ma_trend} | {ma_signal} |
| Bollinger Bands | {bb_position} | {bb_signal} |
| Volatility | {volatility:.2f}% | {volatility_signal} |

**Key Levels:**
- Support: ${support:,.2f}
- Resistance: ${resistance:,.2f}

{technical_summary}

---

## On-Chain Analysis

**Score: {onchain_score:.1f}/100**

| Metric | Value | Signal |
|--------|-------|--------|
| Active Addresses | {active_addresses:,.0f} | {addr_signal} |
| Whale Activity | {whale_signal} | {whale_net_flow} |
| Exchange Flow | {exchange_flow_signal} | - |
| Hash Rate Trend | {hash_rate_trend} | - |
| Gas Fee | {gas_gwei:.0f} gwei | {gas_signal} |

{onchain_summary}

---

## Sentiment Analysis

**Score: {sentiment_score:.1f}/100**

| Indicator | Value | Signal |
|-----------|-------|--------|
| Fear & Greed Index | {fear_greed_value}/100 | {fear_greed_class} |
| Social Activity | - | {social_signal} |
| Google Trends | {trends_latest}/100 | {trends_signal} |
| Funding Rate | {funding_rate_pct:.4f}% | {funding_signal} |
| Long/Short Ratio | {ls_ratio:.2f} | {ls_signal} |

{sentiment_summary}

---

## Macro Economic Analysis

**Score: {macro_score:.1f}/100**

| Indicator | Value | Impact |
|-----------|-------|--------|
| US Dollar Index (DXY) | {dxy_value:.2f} | {dxy_impact} |
| 10Y Treasury Yield | {yield_value:.2f}% | {yield_impact} |
| VIX Fear Index | {vix_value:.2f} | {vix_impact} |
| M2 Money Supply | ${m2_value:.0f}B | {m2_impact} |
| SPX Correlation | {spx_corr:+.2f} | - |

{macro_summary}

---

## Market Structure Analysis

**Score: {ms_score:.1f}/100**

| Metric | Value | Signal |
|--------|-------|--------|
| BTC Dominance | {btc_dominance:.1f}% | {btc_dom_signal} |
| Stablecoin Change | {stable_change:+.1f}% | {stable_signal} |
| Open Interest | ${oi_current:.2f}B | {oi_signal} |
| ETH/BTC Ratio | {eth_btc_ratio:.5f} | {eth_btc_signal} |
| Volume vs Avg | {vol_ratio:.2f}x | {vol_signal} |

{ms_summary}

---

## Key Signals

{key_signals_md}

---

## Conclusion

{conclusion}

---

*⚠️ Disclaimer: This report is for informational purposes only and does not constitute financial advice. Cryptocurrency investments carry significant risk. Always conduct your own research before making investment decisions.*

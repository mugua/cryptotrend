from __future__ import annotations
import uuid
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

_TEMPLATE_PATH = Path(__file__).parent / "templates" / "trend_report.md"


def _safe(v, default=0):
    try:
        return v if v is not None else default
    except Exception:
        return default


class ReportGenerator:
    """Generates trend reports from analysis results."""

    def generate_report(self, coin_id: str, analysis: dict) -> dict:
        report_id = str(uuid.uuid4())
        now = datetime.utcnow()

        tech = analysis.get("technical", {})
        onchain = analysis.get("onchain", {})
        sentiment = analysis.get("sentiment", {})
        macro = analysis.get("macro", {})
        ms = analysis.get("market_structure", {})

        overall_score = float(analysis.get("overall_score", 50.0))
        trend_level = analysis.get("trend_level", "Neutral")
        coin_name = analysis.get("coin_name", coin_id.title())
        current_price = float(analysis.get("current_price", 0))
        price_change_24h = float(analysis.get("price_change_24h", 0))

        key_signals = self._extract_key_signals(analysis)
        executive_summary = self._build_executive_summary(overall_score, trend_level, coin_name, key_signals)
        conclusion = self._build_conclusion(overall_score, trend_level, coin_name)

        markdown_report = self.format_markdown({
            "coin_id": coin_id,
            "coin_name": coin_name,
            "current_price": current_price,
            "price_change_24h": price_change_24h,
            "overall_score": overall_score,
            "trend_level": trend_level,
            "technical": tech,
            "onchain": onchain,
            "sentiment": sentiment,
            "macro": macro,
            "market_structure": ms,
            "factor_scores": analysis.get("factor_scores", []),
            "key_signals": key_signals,
            "executive_summary": executive_summary,
            "conclusion": conclusion,
            "generated_at": now.isoformat(),
        })

        return {
            "id": report_id,
            "coin_id": coin_id,
            "coin_name": coin_name,
            "overall_score": overall_score,
            "trend_level": trend_level,
            "current_price": current_price,
            "price_change_24h": price_change_24h,
            "technical_score": float(tech.get("score", 50)),
            "onchain_score": float(onchain.get("score", 50)),
            "sentiment_score": float(sentiment.get("score", 50)),
            "macro_score": float(macro.get("score", 50)),
            "market_structure_score": float(ms.get("score", 50)),
            "factor_scores": analysis.get("factor_scores", []),
            "technical": tech,
            "onchain": onchain,
            "sentiment": sentiment,
            "macro": macro,
            "market_structure": ms,
            "key_signals": key_signals,
            "executive_summary": executive_summary,
            "conclusion": conclusion,
            "markdown_report": markdown_report,
            "created_at": now.isoformat(),
        }

    def format_markdown(self, report: dict) -> str:
        tech = report.get("technical", {})
        onchain = report.get("onchain", {})
        sentiment = report.get("sentiment", {})
        macro = report.get("macro", {})
        ms = report.get("market_structure", {})
        factor_scores = report.get("factor_scores", [])

        def _factor_score(name: str) -> float:
            for f in factor_scores:
                if f.get("name") == name:
                    return float(f.get("score", 50.0))
            return 50.0

        def _factor_weighted(name: str) -> float:
            for f in factor_scores:
                if f.get("name") == name:
                    return float(f.get("weighted_score", 0.0))
            return 0.0

        def _factor_signal(name: str) -> str:
            for f in factor_scores:
                if f.get("name") == name:
                    return str(f.get("signal", "neutral"))
            return "neutral"

        tech_score = _factor_score("technical")
        onchain_score = _factor_score("onchain")
        sentiment_score = _factor_score("sentiment")
        macro_score = _factor_score("macro")
        ms_score = _factor_score("market_structure")

        # Technical fields
        rsi = float(tech.get("rsi", 50))
        macd = tech.get("macd", {})
        sr = tech.get("support_resistance", {})
        bb = tech.get("bollinger", {})

        # On-chain fields
        addr = onchain.get("active_addresses", {})
        whale = onchain.get("whale_transactions", {})
        flow = onchain.get("exchange_flow", {})
        hr = onchain.get("hash_rate", {})
        gas = onchain.get("gas_fee", {})

        # Sentiment fields
        fg = sentiment.get("fear_greed", {})
        trends = sentiment.get("google_trends", {})
        funding = sentiment.get("funding_rate", {})
        ls = sentiment.get("long_short", {})

        # Macro fields
        dxy = macro.get("dxy", {})
        yield_d = macro.get("treasury_yield", {})
        vix = macro.get("vix", {})
        m2 = macro.get("m2", {})

        # Market structure fields
        btc_dom = ms.get("btc_dominance", {})
        stable = ms.get("stablecoin", {})
        oi = ms.get("open_interest", {})
        eth_btc = ms.get("eth_btc_ratio", {})
        vol = ms.get("volume", {})

        key_signals = report.get("key_signals", [])
        key_signals_md = "\n".join(f"- {s}" for s in key_signals) if key_signals else "- No significant signals detected"

        try:
            template = _TEMPLATE_PATH.read_text()
        except Exception:
            template = _FALLBACK_TEMPLATE

        try:
            return template.format(
                coin_id=report.get("coin_id", ""),
                coin_name=report.get("coin_name", ""),
                current_price=_safe(report.get("current_price"), 0),
                price_change_24h=_safe(report.get("price_change_24h"), 0),
                generated_at=report.get("generated_at", datetime.utcnow().isoformat()),
                overall_score=_safe(report.get("overall_score"), 50),
                trend_level=report.get("trend_level", "Neutral"),
                tech_score=tech_score,
                tech_weighted=_factor_weighted("technical"),
                tech_signal=_factor_signal("technical"),
                onchain_score=onchain_score,
                onchain_weighted=_factor_weighted("onchain"),
                onchain_signal=_factor_signal("onchain"),
                sentiment_score=sentiment_score,
                sentiment_weighted=_factor_weighted("sentiment"),
                sentiment_signal=_factor_signal("sentiment"),
                macro_score=macro_score,
                macro_weighted=_factor_weighted("macro"),
                macro_signal=_factor_signal("macro"),
                ms_score=ms_score,
                ms_weighted=_factor_weighted("market_structure"),
                ms_signal=_factor_signal("market_structure"),
                # Technical
                rsi=rsi,
                rsi_signal="oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral",
                macd_histogram=_safe(macd.get("histogram"), 0),
                macd_signal=tech.get("macd_signal", "neutral"),
                ma_trend=tech.get("ma_trend", "mixed"),
                ma_signal="bullish" if tech.get("ma_trend") == "uptrend" else "bearish" if tech.get("ma_trend") == "downtrend" else "neutral",
                bb_position=tech.get("bollinger_position", "middle"),
                bb_signal="bullish" if tech.get("bollinger_position") == "oversold" else "bearish" if tech.get("bollinger_position") == "overbought" else "neutral",
                volatility=_safe(tech.get("volatility"), 0),
                volatility_signal="low" if _safe(tech.get("volatility"), 3) < 2 else "high" if _safe(tech.get("volatility"), 3) > 5 else "moderate",
                support=_safe(sr.get("support"), 0),
                resistance=_safe(sr.get("resistance"), 0),
                technical_summary=_tech_summary(tech),
                # Onchain
                active_addresses=_safe(addr.get("latest"), 0),
                addr_signal=addr.get("trend", "stable"),
                whale_signal=whale.get("signal", "neutral"),
                whale_net_flow=f"${_safe(whale.get('net_flow_usd'), 0):,.0f}",
                exchange_flow_signal=flow.get("signal", "neutral"),
                hash_rate_trend=hr.get("trend", "stable"),
                gas_gwei=_safe(gas.get("propose_gas_gwei"), 25),
                gas_signal=gas.get("signal", "normal"),
                onchain_summary=_onchain_summary(onchain),
                # Sentiment
                fear_greed_value=_safe(fg.get("raw_value"), 50),
                fear_greed_class=fg.get("classification", "Neutral"),
                social_signal="active" if sentiment_score >= 55 else "quiet",
                trends_latest=_safe(trends.get("latest"), 50),
                trends_signal="rising" if _safe(trends.get("ratio_vs_avg"), 1) > 1.1 else "falling" if _safe(trends.get("ratio_vs_avg"), 1) < 0.9 else "stable",
                funding_rate_pct=_safe(funding.get("rate_pct"), 0.01),
                funding_signal=funding.get("signal", "slightly_positive"),
                ls_ratio=_safe(ls.get("ratio"), 1.0),
                ls_signal=ls.get("signal", "balanced"),
                sentiment_summary=_sentiment_summary(sentiment),
                # Macro
                dxy_value=_safe(dxy.get("latest"), 104),
                dxy_impact=dxy.get("impact", "neutral"),
                yield_value=_safe(yield_d.get("latest"), 4.5),
                yield_impact=yield_d.get("impact", "neutral"),
                vix_value=_safe(vix.get("latest"), 18),
                vix_impact=vix.get("fear_level", "moderate"),
                m2_value=_safe(m2.get("latest_bn_usd"), 21000),
                m2_impact=m2.get("impact", "neutral"),
                spx_corr=_safe(macro.get("correlation_spx"), 0),
                macro_summary=_macro_summary(macro),
                # Market Structure
                btc_dominance=_safe(btc_dom.get("btc_dominance_pct"), 52),
                btc_dom_signal=btc_dom.get("signal", "balanced"),
                stable_change=_safe(stable.get("change_pct"), 0),
                stable_signal=stable.get("signal", "neutral"),
                oi_current=_safe(oi.get("current"), 10e9) / 1e9,
                oi_signal=oi.get("signal", "neutral"),
                eth_btc_ratio=_safe(eth_btc.get("ratio"), 0.05),
                eth_btc_signal=eth_btc.get("signal", "balanced"),
                vol_ratio=_safe(vol.get("ratio_vs_avg"), 1.0),
                vol_signal=vol.get("signal", "average_volume"),
                ms_summary=_ms_summary(ms),
                # Conclusion
                key_signals_md=key_signals_md,
                executive_summary=report.get("executive_summary", ""),
                conclusion=report.get("conclusion", ""),
            )
        except Exception as exc:
            logger.warning("Markdown formatting failed: %s", exc)
            return f"# {report.get('coin_name', '')} Trend Report\n\nOverall Score: {report.get('overall_score', 50)}/100 ({report.get('trend_level', 'Neutral')})\n\nGenerated: {report.get('generated_at', '')}"

    def save_report(self, report: dict) -> None:
        """Persist report to in-memory store (database integration point)."""
        from app.reports import _report_store
        _report_store[report["id"]] = report
        logger.info("Report saved: %s for %s (score=%.1f)", report["id"], report["coin_id"], report["overall_score"])

    def _extract_key_signals(self, analysis: dict) -> list[str]:
        signals = []
        tech = analysis.get("technical", {})
        sentiment = analysis.get("sentiment", {})
        macro = analysis.get("macro", {})
        onchain = analysis.get("onchain", {})

        rsi = float(tech.get("rsi", 50))
        if rsi < 30:
            signals.append(f"🟢 RSI oversold ({rsi:.1f}) — potential reversal opportunity")
        elif rsi > 70:
            signals.append(f"🔴 RSI overbought ({rsi:.1f}) — caution advised")

        macd_sig = tech.get("macd_signal", "neutral")
        if macd_sig == "bullish":
            signals.append("🟢 MACD bullish crossover — positive momentum")
        elif macd_sig == "bearish":
            signals.append("🔴 MACD bearish crossover — negative momentum")

        fg = sentiment.get("fear_greed", {})
        fg_val = int(fg.get("raw_value", 50))
        if fg_val < 25:
            signals.append(f"🟢 Extreme Fear ({fg_val}) — historical buy signal")
        elif fg_val > 75:
            signals.append(f"🔴 Extreme Greed ({fg_val}) — historical sell signal")

        dxy = macro.get("dxy", {})
        dxy_impact = dxy.get("impact", "neutral")
        if dxy_impact == "bullish":
            signals.append("🟢 Weakening DXY — favorable for crypto")
        elif dxy_impact == "bearish":
            signals.append("🔴 Strengthening DXY — headwind for crypto")

        whale = onchain.get("whale_transactions", {})
        if whale.get("signal") == "bullish":
            signals.append("🟢 Whales moving coins off exchanges — accumulation signal")
        elif whale.get("signal") == "bearish":
            signals.append("🔴 Whales moving coins to exchanges — distribution signal")

        if not signals:
            signals.append("⚪ No exceptional signals detected — market in consolidation")

        return signals

    def _build_executive_summary(self, score: float, level: str, coin_name: str, signals: list[str]) -> str:
        bullish_signals = sum(1 for s in signals if "🟢" in s)
        bearish_signals = sum(1 for s in signals if "🔴" in s)
        summary = f"{coin_name} currently shows a **{level}** trend with an overall score of **{score:.1f}/100**. "
        if bullish_signals > bearish_signals:
            summary += f"There are {bullish_signals} bullish and {bearish_signals} bearish signals active. "
            summary += "The weight of evidence favors buyers at current levels."
        elif bearish_signals > bullish_signals:
            summary += f"There are {bearish_signals} bearish and {bullish_signals} bullish signals active. "
            summary += "Caution is warranted; the evidence favors sellers at current levels."
        else:
            summary += "The market shows mixed signals with no clear directional bias."
        return summary

    def _build_conclusion(self, score: float, level: str, coin_name: str) -> str:
        if score >= 75:
            return (f"The analysis strongly favors a **{level}** stance on {coin_name}. "
                    "Multiple indicators align bullishly. Monitor for continuation signals.")
        elif score >= 60:
            return (f"The analysis suggests a **{level}** bias for {coin_name}. "
                    "Conditions favor bulls but remain watchful of macro headwinds.")
        elif score >= 40:
            return (f"The market for {coin_name} is **Neutral**. "
                    "Traders should exercise caution and wait for clearer directional signals.")
        elif score >= 25:
            return (f"The analysis indicates a **{level}** environment for {coin_name}. "
                    "Defensive positioning may be prudent until conditions improve.")
        else:
            return (f"Multiple indicators signal a **{level}** environment for {coin_name}. "
                    "High caution is advised; risk management should be prioritized.")


# ── Summary helpers ────────────────────────────────────────────────────────────

def _tech_summary(tech: dict) -> str:
    rsi = float(tech.get("rsi", 50))
    ma_trend = tech.get("ma_trend", "mixed")
    return (f"RSI at {rsi:.1f} indicates {'oversold conditions' if rsi < 30 else 'overbought conditions' if rsi > 70 else 'neutral momentum'}. "
            f"Moving average analysis shows a {ma_trend} trend.")


def _onchain_summary(onchain: dict) -> str:
    addr = onchain.get("active_addresses", {})
    return f"Active address trend: **{addr.get('trend', 'stable')}** (ratio vs 30d avg: {addr.get('ratio_vs_avg', 1.0):.3f})."


def _sentiment_summary(sentiment: dict) -> str:
    fg = sentiment.get("fear_greed", {})
    return (f"Market sentiment is **{fg.get('classification', 'Neutral')}** "
            f"(Fear & Greed: {fg.get('raw_value', 50)}). "
            "Contrarian analysis suggests monitoring for reversals at extremes.")


def _macro_summary(macro: dict) -> str:
    dxy = macro.get("dxy", {})
    vix = macro.get("vix", {})
    return (f"Macro environment: DXY at {dxy.get('latest', 104):.2f} ({dxy.get('impact', 'neutral')} for crypto), "
            f"VIX at {vix.get('latest', 18):.2f} ({vix.get('fear_level', 'moderate')} fear).")


def _ms_summary(ms: dict) -> str:
    btc_dom = ms.get("btc_dominance", {})
    vol = ms.get("volume", {})
    return (f"BTC dominance at {btc_dom.get('btc_dominance_pct', 52):.1f}% ({btc_dom.get('signal', 'balanced')}). "
            f"Volume is {vol.get('ratio_vs_avg', 1.0):.2f}x the 30-day average.")


_FALLBACK_TEMPLATE = "# {coin_name} Trend Report\n\nScore: {overall_score}/100 | {trend_level}\n\nGenerated: {generated_at}\n"

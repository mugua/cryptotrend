from __future__ import annotations
import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


# ── Job functions ──────────────────────────────────────────────────────────────

async def _update_prices() -> None:
    from app.collectors import CoinGeckoCollector
    from app.config import get_settings

    settings = get_settings()
    try:
        cg = CoinGeckoCollector()
        prices = await cg.fetch_prices(settings.tracked_coins)
        logger.info("[scheduler] prices updated for %d coins at %s", len(prices), datetime.utcnow().isoformat())
    except Exception as exc:
        logger.warning("[scheduler] price update failed: %s", exc)


async def _update_onchain_sentiment() -> None:
    from app.collectors import (
        BlockchainCollector,
        EtherscanCollector,
        FearGreedCollector,
        RedditCollector,
        WhaleAlertCollector,
    )

    try:
        bc = BlockchainCollector()
        es = EtherscanCollector()
        fg = FearGreedCollector()
        rd = RedditCollector()
        wh = WhaleAlertCollector()

        await asyncio.gather(
            bc.fetch_active_addresses(),
            bc.fetch_hash_rate(),
            es.fetch_gas_price(),
            fg.fetch_current(),
            rd.fetch_subreddit_stats("bitcoin"),
            rd.fetch_subreddit_stats("ethereum"),
            wh.fetch_recent_transactions(),
            return_exceptions=True,
        )
        logger.info("[scheduler] on-chain + sentiment updated at %s", datetime.utcnow().isoformat())
    except Exception as exc:
        logger.warning("[scheduler] on-chain/sentiment update failed: %s", exc)


async def _update_macro() -> None:
    from app.collectors import FREDCollector, YahooFinanceCollector

    try:
        fred = FREDCollector()
        yf = YahooFinanceCollector()

        await asyncio.gather(
            fred.fetch_dxy(),
            fred.fetch_treasury_yield(),
            fred.fetch_vix(),
            fred.fetch_m2(),
            yf.fetch_spx(),
            yf.fetch_vix(),
            yf.fetch_dxy(),
            yf.fetch_gold(),
            return_exceptions=True,
        )
        logger.info("[scheduler] macro data updated at %s", datetime.utcnow().isoformat())
    except Exception as exc:
        logger.warning("[scheduler] macro update failed: %s", exc)


async def _generate_trend_reports() -> None:
    from app.engine import TrendScorer
    from app.reports import ReportGenerator

    scorer = TrendScorer()
    generator = ReportGenerator()

    for coin_id in ["bitcoin", "ethereum"]:
        try:
            analysis = await scorer.generate_full_analysis(coin_id)
            report = generator.generate_report(coin_id, analysis)
            generator.save_report(report)
            logger.info("[scheduler] trend report generated for %s (score=%.1f)", coin_id, report["overall_score"])
        except Exception as exc:
            logger.warning("[scheduler] report generation failed for %s: %s", coin_id, exc)


# ── Wrapper to run async jobs from APScheduler ─────────────────────────────────

def _run_async(coro_func):
    async def wrapper():
        await coro_func()
    return wrapper


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return

    _scheduler = AsyncIOScheduler()

    # Every 5 minutes: update prices
    _scheduler.add_job(
        _update_prices,
        trigger=IntervalTrigger(minutes=5),
        id="update_prices",
        name="Update coin prices",
        replace_existing=True,
        misfire_grace_time=60,
    )

    # Every 1 hour: update on-chain + sentiment
    _scheduler.add_job(
        _update_onchain_sentiment,
        trigger=IntervalTrigger(hours=1),
        id="update_onchain_sentiment",
        name="Update on-chain and sentiment",
        replace_existing=True,
        misfire_grace_time=300,
    )

    # Every 6 hours: update macro
    _scheduler.add_job(
        _update_macro,
        trigger=IntervalTrigger(hours=6),
        id="update_macro",
        name="Update macro data",
        replace_existing=True,
        misfire_grace_time=1800,
    )

    # Every 24 hours: generate trend reports
    _scheduler.add_job(
        _generate_trend_reports,
        trigger=IntervalTrigger(hours=24),
        id="generate_reports",
        name="Generate daily trend reports",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    _scheduler.start()
    logger.info("APScheduler started with %d jobs", len(_scheduler.get_jobs()))


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")

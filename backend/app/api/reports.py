from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException

from app.reports import ReportGenerator, _report_store
from app.engine import TrendScorer

logger = logging.getLogger(__name__)
router = APIRouter()

_scorer = TrendScorer()
_generator = ReportGenerator()


@router.get("/")
async def list_reports(limit: int = 20):
    reports = sorted(_report_store.values(), key=lambda r: r["created_at"], reverse=True)[:limit]
    return {"reports": [{"id": r["id"], "coin_id": r["coin_id"], "coin_name": r["coin_name"], "overall_score": r["overall_score"], "trend_level": r["trend_level"], "created_at": r["created_at"]} for r in reports], "total": len(reports)}


@router.get("/{report_id}")
async def get_report(report_id: str):
    report = _report_store.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")
    return report


@router.post("/generate/{coin_id}")
async def generate_report(coin_id: str):
    try:
        analysis = await _scorer.generate_full_analysis(coin_id)
        report = _generator.generate_report(coin_id, analysis)
        _generator.save_report(report)
        return {"id": report["id"], "coin_id": report["coin_id"], "overall_score": report["overall_score"], "trend_level": report["trend_level"], "created_at": report["created_at"]}
    except Exception as exc:
        logger.error("generate_report failed for %s: %s", coin_id, exc)
        raise HTTPException(status_code=502, detail=str(exc))

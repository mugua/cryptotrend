from app.reports.generator import ReportGenerator

# In-memory report store (replace with DB in production)
_report_store: dict[str, dict] = {}

__all__ = ["ReportGenerator", "_report_store"]

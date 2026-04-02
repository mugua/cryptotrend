from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api import market_router, analysis_router, reports_router
from app.scheduler import start_scheduler, stop_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Cryptocurrency trend analysis backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market_router, prefix="/api/market", tags=["Market"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}

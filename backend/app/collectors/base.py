from __future__ import annotations
import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token-bucket rate limiter (async)."""

    def __init__(self, rate: float) -> None:
        self.rate = rate  # requests per second
        self._min_interval = 1.0 / rate
        self._last_call = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            if elapsed < self._min_interval:
                await asyncio.sleep(self._min_interval - elapsed)
            self._last_call = time.monotonic()


class SimpleCache:
    """Minimal in-memory TTL cache."""

    def __init__(self, default_ttl: int = 300) -> None:
        self.default_ttl = default_ttl
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        self._store[key] = (value, time.monotonic() + ttl)

    def clear(self) -> None:
        self._store.clear()


class BaseCollector(ABC):
    """Abstract base for all data collectors."""

    BASE_URL: str = ""
    DEFAULT_TIMEOUT: float = 15.0
    DEFAULT_HEADERS: dict[str, str] = {
        "User-Agent": "CryptoTrend/1.0 (https://github.com/cryptotrend)"
    }

    def __init__(self, rate_limit: float = 1.0, cache_ttl: int = 300) -> None:
        self._rate_limiter = RateLimiter(rate_limit)
        self._cache = SimpleCache(default_ttl=cache_ttl)

    # ------------------------------------------------------------------ helpers

    async def _get(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Any:
        await self._rate_limiter.acquire()
        merged_headers = {**self.DEFAULT_HEADERS, **(headers or {})}
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, params=params, headers=merged_headers)
            response.raise_for_status()
            return response.json()

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=False,
    )
    async def _get_with_retry(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Optional[Any]:
        return await self._get(url, params=params, headers=headers, timeout=timeout)

    async def fetch_cached(
        self, cache_key: str, fetch_fn, ttl: Optional[int] = None
    ) -> Any:
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        result = await fetch_fn()
        if result is not None:
            self._cache.set(cache_key, result, ttl)
        return result

    @abstractmethod
    async def fetch(self) -> Any:
        """Entry-point fetch method implemented by each subclass."""

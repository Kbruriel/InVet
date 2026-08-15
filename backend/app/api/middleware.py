"""Simple in-memory rate limiting middleware.

This is a lightweight, process-local rate limiter intended as a configurable
mitigation for brute-force endpoints (auth, login). It is NOT a replacement
for production-grade rate limiting (use API Gateway / Redis-backed limiters).
"""
from __future__ import annotations

import time
from typing import Dict, List

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basic sliding-window per-key rate limiter.

    Configurable via keyword args when added as middleware. Default limits are
    conservative for login/register endpoints.
    """

    def __init__(self, app, calls: int = 5, period: int = 10, key_prefix: str = "rl") -> None:
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.key_prefix = key_prefix
        # map key -> list[timestamps]
        self._store: Dict[str, List[float]] = {}

    def _get_client_ip(self, request: Request) -> str:
        # Respect X-Forwarded-For when present (API gateway sets it).
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        # Only apply to mutating or auth-related endpoints to limit impact.
        if request.method.upper() not in ("POST", "PUT", "PATCH", "DELETE"):
            return await call_next(request)

        path = request.url.path or "/"
        # Reduce granularity: only enforce for auth endpoints and login/register paths
        if not (path.startswith("/api/v1/auth") or path.startswith("/api/v1/auth")):
            return await call_next(request)

        client = self._get_client_ip(request)
        key = f"{self.key_prefix}:{client}:{path}"
        now = time.time()
        window_start = now - self.period

        entries = self._store.get(key, [])
        # Remove timestamps outside window
        entries = [t for t in entries if t >= window_start]
        entries.append(now)
        self._store[key] = entries

        if len(entries) > self.calls:
            # Too many requests
            retry_after = int(entries[0] + self.period - now)
            return JSONResponse(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests, try again later.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)

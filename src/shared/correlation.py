import logging
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)

HEADER_NAME = "X-Correlation-Id"


def get_correlation_id() -> str:
    """Returns the active request correlation id, or a new UUID if unset (e.g. background work)."""
    cid = _correlation_id.get()
    if cid is None:
        return str(uuid.uuid4())
    return cid


def correlation_http_headers() -> dict[str, str]:
    return {HEADER_NAME: get_correlation_id()}


class CorrelationIdFilter(logging.Filter):
    """Injects correlation_id on log records for formatter use."""

    def filter(self, record: logging.LogRecord) -> bool:
        cid = _correlation_id.get()
        record.correlation_id = cid if cid is not None else "-"
        return True


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        raw = request.headers.get(HEADER_NAME) or request.headers.get(
            HEADER_NAME.lower()
        )
        correlation_id = raw.strip() if raw else str(uuid.uuid4())
        token = _correlation_id.set(correlation_id)
        try:
            response = await call_next(request)
        finally:
            _correlation_id.reset(token)
        response.headers[HEADER_NAME] = correlation_id
        return response

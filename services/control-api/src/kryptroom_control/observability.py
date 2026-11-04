"""Allowlisted request metadata only: never body, query, credentials or exception text."""

import json
import logging
import time
from uuid import uuid4

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("kryptroom_control.http")


def configure_request_logging() -> None:
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class CorrelationMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        correlation_id = str(uuid4())
        scope.setdefault("state", {})["correlation_id"] = correlation_id
        started = time.monotonic()
        status = 500
        response_started = False

        async def send_with_id(message: Message) -> None:
            nonlocal status, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status = message["status"]
                message.setdefault("headers", []).extend(
                    [
                        (b"x-correlation-id", correlation_id.encode("ascii")),
                        (b"cache-control", b"no-store"),
                        (b"x-content-type-options", b"nosniff"),
                    ]
                )
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception:
            if response_started:
                raise
            # Handle before ServerErrorMiddleware/Uvicorn can emit an exception traceback
            # containing a credential-bearing driver exception. No streaming routes in PR1.
            response = JSONResponse(
                status_code=500,
                content={
                    "error": {"code": "internal_error", "message": "An internal error occurred"},
                    "correlation_id": correlation_id,
                },
            )
            await response(scope, receive, send_with_id)
        finally:
            # Route templates are server-defined; unmatched paths are never logged verbatim.
            route = getattr(scope.get("route"), "path", "unmatched")
            method = scope.get("method", "OTHER")
            if method not in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}:
                method = "OTHER"
            logger.info(
                json.dumps(
                    {
                        "event": "http_request",
                        "correlation_id": correlation_id,
                        "method": method,
                        "route": route,
                        "status": status,
                        "duration_ms": round((time.monotonic() - started) * 1000, 2),
                    },
                    separators=(",", ":"),
                )
            )

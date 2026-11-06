from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException

from kryptroom_control.config import Settings, load_settings
from kryptroom_control.contracts import BusinessError, ErrorDetail, ErrorResponse, HealthResponse
from kryptroom_control.db import Database
from kryptroom_control.observability import CorrelationMiddleware, configure_request_logging


def error_response(request: Request, status: int, code: str, message: str) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorDetail(code=code, message=message),
        correlation_id=request.state.correlation_id,
    )
    return JSONResponse(status_code=status, content=body.model_dump(mode="json"))


def create_app(settings: Settings | None = None) -> FastAPI:
    configuration = settings if settings is not None else load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_request_logging()
        app.state.database = Database(configuration)
        try:
            yield
        finally:
            app.state.database.close()

    app = FastAPI(
        title="KryptRoom Control API — Foundation",
        version="0.1.0",
        description=(
            "Technical health only. No authentication, business resources, "
            "cryptographic execution, disclosure or anchoring API in M9-PR1."
        ),
        lifespan=lifespan,
        debug=False,
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json" if configuration.docs_enabled else None,
    )
    app.add_middleware(CorrelationMiddleware)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        # Ignore exception detail/headers: callers must never reflect submitted values.
        code = "resource_not_found" if exc.status_code == 404 else "http_error"
        return error_response(request, exc.status_code, code, "Request could not be served")

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(request, 422, "validation_error", "Request validation failed")

    @app.exception_handler(BusinessError)
    async def business_error(request: Request, exc: BusinessError) -> JSONResponse:
        status = {"permission_denied": 403, "resource_not_found": 404, "conflict": 409}[exc.code]
        return error_response(request, status, exc.code, "Request could not be completed")

    @app.get("/health/live", response_model=HealthResponse, tags=["health"])
    def live() -> HealthResponse:
        return HealthResponse(status="alive")

    @app.get(
        "/health/ready",
        response_model=HealthResponse,
        tags=["health"],
        responses={
            503: {"model": ErrorResponse, "description": "Dependency or schema unavailable"}
        },
    )
    def ready(request: Request) -> Any:
        try:
            available = request.app.state.database.ready()
        except SQLAlchemyError:
            available = False
        if not available:
            return error_response(request, 503, "not_ready", "Service is not ready")
        return HealthResponse(status="ready")

    return app

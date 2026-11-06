"""Wire conventions for future metadata APIs; not cryptographic contracts."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class ErrorDetail(Contract):
    code: str
    message: str


class ErrorResponse(Contract):
    error: ErrorDetail
    correlation_id: UUID


class DataResponse[T](Contract):
    data: T
    correlation_id: UUID


class PageRequest(Contract):
    limit: int = Field(default=25, ge=1, le=100)
    # Opaque bounded cursor; not decoded or trusted as an authorization token.
    cursor: str | None = Field(default=None, min_length=1, max_length=512)


class Page[T](Contract):
    items: tuple[T, ...]
    next_cursor: str | None = None


class HealthResponse(Contract):
    status: Literal["alive", "ready"]


class BusinessError(Exception):
    def __init__(self, code: Literal["permission_denied", "resource_not_found", "conflict"]):
        self.code = code
        super().__init__(code)

"""Authenticated persistent draft Rooms. No cryptographic execution authority."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse
from pydantic import ConfigDict, Field

from kryptroom_control.contracts import Contract, DataResponse, Page
from kryptroom_control.identity_api import Limit, Service, response
from kryptroom_control.identity_api import router as identity_router
from kryptroom_control.organization_service import AccessError
from kryptroom_control.room_service import RoomService

router = APIRouter(
    prefix="/api/v1",
    tags=["rooms"],
    dependencies=identity_router.dependencies,
    responses=identity_router.responses,
)
Label = Annotated[str, Field(min_length=1, max_length=120, pattern=r"^[^\x00-\x1f\x7f]+$")]
Description = Annotated[str, Field(max_length=1000, pattern=r"^[^\x00-\x1f\x7f]*$")]


class RoomInput(Contract):
    model_config = ConfigDict(
        extra="forbid", frozen=True, hide_input_in_errors=True, str_strip_whitespace=True
    )
    displayName: Label
    description: Description = ""


class RoomPatch(Contract):
    model_config = RoomInput.model_config
    displayName: Label | None = None
    description: Description | None = None


class RoomOutput(Contract):
    id: UUID
    organizationId: UUID
    displayName: str
    description: str
    status: Literal["DRAFT"]
    headStateId: None = None
    version: int


@router.post(
    "/organizations/{organizationId}/rooms",
    status_code=201,
    response_model=DataResponse[RoomOutput],
)
def create_room(
    request: Request,
    organizationId: UUID,
    body: RoomInput,
    service: Service,
    idempotency_key: Annotated[str | None, Header(max_length=128)] = None,
) -> JSONResponse:
    if not idempotency_key or not idempotency_key.strip():
        raise AccessError(428, "idempotency_key_required")
    data = RoomService(service).create(
        organizationId, body.displayName, body.description, idempotency_key
    )
    return response(request, data, 201)


@router.get("/organizations/{organizationId}/rooms", response_model=DataResponse[Page[RoomOutput]])
def list_rooms(
    request: Request,
    organizationId: UUID,
    service: Service,
    limit: Limit = 25,
    cursor: UUID | None = None,
) -> JSONResponse:
    return response(request, RoomService(service).listing(organizationId, limit, cursor))


@router.get("/rooms/{roomId}", response_model=DataResponse[RoomOutput])
def read_room(request: Request, roomId: UUID, service: Service) -> JSONResponse:
    return response(request, RoomService(service).read(roomId))


@router.patch("/rooms/{roomId}", response_model=DataResponse[RoomOutput])
def update_room(
    request: Request,
    roomId: UUID,
    body: RoomPatch,
    service: Service,
    if_match: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    changes = body.model_dump(exclude_unset=True)
    if not changes or any(value is None for value in changes.values()):
        raise AccessError(422, "invalid_room_metadata")
    return response(request, RoomService(service).update(roomId, changes, if_match))

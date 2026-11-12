from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse

from kryptroom_control.collaboration import Collaboration
from kryptroom_control.contracts import Contract, DataResponse, Page
from kryptroom_control.identity_api import Limit, Service, response
from kryptroom_control.identity_api import router as identity_router
from kryptroom_control.organization_service import AccessError
from kryptroom_control.room_service import RoomService

router = APIRouter(
    prefix="/api/v1",
    tags=["room-collaboration"],
    dependencies=identity_router.dependencies,
    responses=identity_router.responses,
)


class Invite(Contract):
    organizationId: UUID
    targetOrganizationId: UUID


class Transition(Contract):
    roomId: UUID
    action: Literal["accept", "reject", "revoke", "leave"]


class InvitationOutput(Contract):
    id: UUID
    roomId: UUID
    ownerOrganizationId: UUID
    targetOrganizationId: UUID
    status: Literal["PENDING", "ACCEPTED", "REJECTED", "REVOKED", "LEFT"]
    version: int


class ParticipantsOutput(Contract):
    ownerOrganizationId: UUID
    partnerOrganizationIds: tuple[UUID, ...]


class HistoryOutput(Contract):
    id: UUID
    kind: Literal[
        "room_created",
        "room_metadata_updated",
        "invitation_invite",
        "invitation_accept",
        "invitation_reject",
        "invitation_leave",
        "invitation_revoke",
    ]
    actorOrganizationId: UUID
    createdAt: datetime


@router.get("/rooms/{roomId}/history", response_model=DataResponse[Page[HistoryOutput]])
def history(
    request: Request, roomId: UUID, service: Service, limit: Limit = 25, cursor: UUID | None = None
) -> JSONResponse:
    RoomService(service).read(roomId)
    return response(request, Collaboration(service).history(roomId, limit, cursor))


@router.post(
    "/rooms/{roomId}/invitations", status_code=201, response_model=DataResponse[InvitationOutput]
)
def invite(
    request: Request,
    roomId: UUID,
    body: Invite,
    service: Service,
    idempotency_key: Annotated[str | None, Header(max_length=128)] = None,
) -> JSONResponse:
    if not idempotency_key or not idempotency_key.strip():
        raise AccessError(428, "idempotency_key_required")
    return response(
        request,
        Collaboration(service).mutate(
            body.organizationId,
            roomId,
            "invite",
            target=body.targetOrganizationId,
            key=idempotency_key,
        ),
        201,
    )


@router.get(
    "/organizations/{organizationId}/room-invitations",
    response_model=DataResponse[Page[InvitationOutput]],
)
def invitations(
    request: Request,
    organizationId: UUID,
    service: Service,
    limit: Limit = 25,
    cursor: UUID | None = None,
) -> JSONResponse:
    return response(request, Collaboration(service).listing(organizationId, limit, cursor))


@router.patch(
    "/organizations/{organizationId}/room-invitations/{invitationId}",
    response_model=DataResponse[InvitationOutput],
)
def transition(
    request: Request,
    organizationId: UUID,
    invitationId: UUID,
    body: Transition,
    service: Service,
    if_match: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    return response(
        request,
        Collaboration(service).mutate(
            organizationId, body.roomId, body.action, iid=invitationId, etag=if_match
        ),
    )


@router.get("/rooms/{roomId}/participants", response_model=DataResponse[ParticipantsOutput])
def participants(request: Request, roomId: UUID, service: Service) -> JSONResponse:
    room = RoomService(service).read(roomId)
    # Narrow definer projection: no access to private organization records.
    targets = (
        service.session.execute(
            sa.text("SELECT * FROM control_api.room_participants(:rid)"), {"rid": roomId}
        )
        .scalars()
        .all()
    )
    return response(
        request,
        {
            "ownerOrganizationId": room["organizationId"],
            "partnerOrganizationIds": [str(t) for t in targets],
        },
    )

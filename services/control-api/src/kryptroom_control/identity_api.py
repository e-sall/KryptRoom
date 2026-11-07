"""Explicit PR2 metadata routes. No runtime or cryptographic authorization."""

from collections.abc import Iterator
from typing import Annotated, Any, Literal
from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import ConfigDict, Field, SecretStr
from uuid6 import uuid7

from kryptroom_control.contracts import Contract, DataResponse, ErrorResponse, Page
from kryptroom_control.identity_schema import memberships, organizations
from kryptroom_control.modules.authorization import BusinessAction
from kryptroom_control.modules.identity import Principal
from kryptroom_control.oidc import AuthenticationFailed, IdentityProviderUnavailable
from kryptroom_control.organization_service import (
    AccessError,
    OrganizationService,
    active_user,
    member_wire,
    org_wire,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["identity-organizations"],
    dependencies=[Depends(HTTPBearer(auto_error=False))],
    responses={status: {"model": ErrorResponse} for status in (401, 403, 404, 409, 412, 428, 503)},
)


class EmptyInput(Contract):
    pass


class OrganizationInput(Contract):
    model_config = ConfigDict(
        extra="forbid", frozen=True, hide_input_in_errors=True, str_strip_whitespace=True
    )
    displayName: str = Field(min_length=1, max_length=120, pattern=r"^[^\x00-\x1f\x7f]+$")


class RoleInput(Contract):
    role: Literal["ORG_OWNER", "ORG_ADMIN", "ORG_MEMBER"]


class OrganizationOutput(Contract):
    id: UUID
    displayName: str
    status: Literal["PENDING_REVIEW", "ACTIVE", "SUSPENDED", "REJECTED"]
    verificationStatus: Literal["UNVERIFIED", "REVIEWED"]
    version: int


class MemberOutput(Contract):
    id: UUID
    organizationId: UUID
    userId: UUID
    role: Literal["ORG_OWNER", "ORG_ADMIN", "ORG_MEMBER"]
    status: Literal["PENDING", "ACTIVE", "REVOKED"]
    version: int


class IdentityOutput(Contract):
    id: UUID
    displayName: str
    status: Literal["ACTIVE", "SUSPENDED"]


class MeOutput(IdentityOutput):
    organizations: tuple[OrganizationOutput, ...]
    memberships: tuple[MemberOutput, ...]


def identity(request: Request) -> Any:
    value = request.headers.get("authorization", "")
    if not value.startswith("Bearer ") or not value[7:] or " " in value[7:]:
        raise AccessError(401, "authentication_required")
    try:
        return request.app.state.oidc.verify_access_token(SecretStr(value[7:]))
    except AuthenticationFailed:
        raise AccessError(401, "authentication_failed") from None
    except IdentityProviderUnavailable:
        raise AccessError(503, "identity_provider_unavailable") from None


def transaction(request: Request) -> Iterator[OrganizationService]:
    verified = identity(request)
    with request.app.state.database.transaction() as session:
        uid = session.scalar(
            sa.text("SELECT control_api.lookup_identity(:iss,:sub)"),
            {"iss": verified.issuer, "sub": verified.subject},
        )
        if uid is None:
            raise AccessError(401, "identity_unknown")
        active_user(session, uid)
        yield OrganizationService(session, Principal(uid))


Service = Annotated[OrganizationService, Depends(transaction, scope="function")]
Limit = Annotated[int, Query(ge=1, le=100)]


def response(request: Request, data: Any, status: int = 200) -> JSONResponse:
    headers = {"Cache-Control": "private, no-store"}
    if isinstance(data, dict) and "version" in data:
        headers["ETag"] = f'"{data["version"]}"'
    return JSONResponse(
        {"data": data, "correlation_id": request.state.correlation_id},
        status_code=status,
        headers=headers,
    )


@router.post("/auth/complete", response_model=DataResponse[IdentityOutput])
def complete(request: Request, body: EmptyInput | None = None) -> JSONResponse:
    verified = identity(request)
    with request.app.state.database.transaction() as session:
        uid = session.scalar(
            sa.text("SELECT control_api.resolve_identity(:uid,:lid,:iss,:sub,:label,:email)"),
            {
                "uid": uuid7(),
                "lid": uuid7(),
                "iss": verified.issuer,
                "sub": verified.subject,
                "label": verified.display_name,
                "email": verified.email_snapshot,
            },
        )
        user = active_user(session, uid)
        data = {"id": str(uid), "displayName": user["display_name"], "status": user["status"]}
    return response(request, data)


@router.get("/me", response_model=DataResponse[MeOutput])
def me(request: Request, service: Service) -> JSONResponse:
    user = active_user(service.session, service.principal.user_id)
    own_memberships = (
        service.session.execute(
            sa.select(memberships)
            .join(organizations, organizations.c.id == memberships.c.organization_id)
            .where(
                memberships.c.user_id == service.principal.user_id,
                memberships.c.status == "ACTIVE",
                organizations.c.status == "ACTIVE",
            )
            .order_by(memberships.c.id)
        )
        .mappings()
        .all()
    )
    return response(
        request,
        {
            "id": str(user["id"]),
            "displayName": user["display_name"],
            "status": user["status"],
            "organizations": service.listing()["items"],
            "memberships": [member_wire(row) for row in own_memberships],
        },
    )


@router.get("/me/registrations", response_model=DataResponse[Page[OrganizationOutput]])
def registrations(
    request: Request, service: Service, limit: Limit = 25, cursor: UUID | None = None
) -> JSONResponse:
    return response(request, service.listing(registrations=True, limit=limit, cursor=cursor))


@router.get("/organizations", response_model=DataResponse[Page[OrganizationOutput]])
def list_organizations(
    request: Request, service: Service, limit: Limit = 25, cursor: UUID | None = None
) -> JSONResponse:
    return response(request, service.listing(limit=limit, cursor=cursor))


@router.post("/organizations", status_code=202, response_model=DataResponse[OrganizationOutput])
def register(
    request: Request,
    body: OrganizationInput,
    service: Service,
    idempotency_key: Annotated[str | None, Header(max_length=128)] = None,
) -> JSONResponse:
    if idempotency_key is None or not idempotency_key.strip():
        raise AccessError(428, "idempotency_key_required")
    return response(request, service.register(body.displayName, idempotency_key), 202)


@router.get("/organizations/{organizationId}", response_model=DataResponse[OrganizationOutput])
def read_organization(request: Request, organizationId: UUID, service: Service) -> JSONResponse:
    org, _ = service.authorized(organizationId, BusinessAction.ORGANIZATION_READ)
    return response(request, org_wire(org))


@router.patch("/organizations/{organizationId}", response_model=DataResponse[OrganizationOutput])
def update_organization(
    request: Request,
    organizationId: UUID,
    body: OrganizationInput,
    service: Service,
    if_match: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    return response(request, service.rename(organizationId, body.displayName, if_match))


@router.get(
    "/organizations/{organizationId}/members", response_model=DataResponse[Page[MemberOutput]]
)
def list_members(
    request: Request,
    organizationId: UUID,
    service: Service,
    limit: Limit = 25,
    cursor: UUID | None = None,
) -> JSONResponse:
    return response(request, service.member_listing(organizationId, limit, cursor))


@router.patch(
    "/organizations/{organizationId}/members/{membershipId}",
    response_model=DataResponse[MemberOutput],
)
def change_role(
    request: Request,
    organizationId: UUID,
    membershipId: UUID,
    body: RoleInput,
    service: Service,
    if_match: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    return response(
        request, service.change_member(organizationId, membershipId, body.role, if_match)
    )


@router.delete(
    "/organizations/{organizationId}/members/{membershipId}",
    response_model=DataResponse[MemberOutput],
)
def revoke(
    request: Request,
    organizationId: UUID,
    membershipId: UUID,
    service: Service,
    if_match: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    return response(request, service.change_member(organizationId, membershipId, None, if_match))

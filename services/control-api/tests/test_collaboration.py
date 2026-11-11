from uuid import uuid4

import pytest
from pydantic import ValidationError

from kryptroom_control.collaboration_api import InvitationOutput, Invite, Transition


def test_collaboration_input_never_grants_client_authority():
    base = {"organizationId": uuid4(), "targetOrganizationId": uuid4()}
    assert Invite(**base).targetOrganizationId == base["targetOrganizationId"]
    for extra in ({"status": "ACCEPTED"}, {"role": "ORG_OWNER"}, {"headStateId": uuid4()}):
        with pytest.raises(ValidationError):
            Invite(**base, **extra)
    for action in ("run", "prove", "reveal", "approve"):
        with pytest.raises(ValidationError):
            Transition(roomId=uuid4(), action=action)


def test_invitation_output_is_narrow_metadata_only():
    fields = set(InvitationOutput.model_fields)
    assert fields == {
        "id",
        "roomId",
        "ownerOrganizationId",
        "targetOrganizationId",
        "status",
        "version",
    }

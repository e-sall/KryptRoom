from typing import Protocol
from uuid import UUID


class RoomDirectory(Protocol):
    """Future metadata Rooms, not RoomStates; exactly two participating organizations in M9."""

    def is_active_participant(self, room_id: UUID, organization_id: UUID) -> bool: ...

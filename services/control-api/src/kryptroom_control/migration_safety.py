"""Release policy: preserve history unless resetting an explicit test fixture."""

from alembic.config import Config
from alembic.script import ScriptDirectory

from kryptroom_control.config import Settings

HISTORY_REVISION = "0006_room_history"


def protect_history(
    settings: Settings,
    config: Config,
    current_heads: tuple[str, ...],
    target: str | tuple[str, ...] | None,
) -> None:
    if target is None:
        return  # inspection/autogeneration does not request a migration destination
    script = ScriptDirectory.from_config(config)

    def ancestry(heads: tuple[str, ...]) -> set[str]:
        return {r.revision for head in heads for r in script.iterate_revisions(head, "base")}

    destination = tuple(r.revision for r in script.get_revisions(target))
    if HISTORY_REVISION not in ancestry(current_heads) or HISTORY_REVISION in ancestry(destination):
        return
    disposable = config.attributes.get("allow_disposable_history_loss") is True
    if not (
        disposable and settings.environment == "test" and settings.database_name.endswith("_test")
    ):
        raise RuntimeError("History-losing downgrade blocked; use a reviewed forward migration")

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    MetaData,
    String,
    create_engine,
    func,
    text,
    true,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from kryptroom_control.config import Settings

SCHEMA = "control_api"
SCHEMA_REVISION = "0001_foundation"
SCHEMA_CONTRACT = "m9-control-foundation-v1"


class Base(DeclarativeBase):
    metadata = MetaData(
        schema=SCHEMA,
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        },
    )


class FoundationMetadata(Base):
    __tablename__ = "foundation_metadata"
    __table_args__ = (
        CheckConstraint("singleton = true", name="singleton"),
        CheckConstraint("contract = 'm9-control-foundation-v1'", name="contract"),
    )

    singleton: Mapped[bool] = mapped_column(Boolean, primary_key=True, server_default=true())
    contract: Mapped[str] = mapped_column(String(48), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Database:
    def __init__(self, settings: Settings) -> None:
        self.engine = create_engine(
            settings.database_url(),
            echo=False,
            hide_parameters=True,
            pool_pre_ping=True,
            pool_size=settings.database_pool_size,
            max_overflow=0,
            pool_timeout=2,
            connect_args={
                "connect_timeout": settings.database_connect_timeout,
                "options": f"-c statement_timeout={settings.database_statement_timeout_ms}",
                "application_name": "kryptroom-control-api",
            },
        )
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)

    @contextmanager
    def transaction(self) -> Iterator[Session]:
        """Commit only a successful unit of work; rollback/close on every exception."""
        with self.sessions.begin() as session:
            yield session

    def ready(self) -> bool:
        # No automatic migrations at application startup, and no metadata mutation here.
        with self.engine.connect() as connection:
            version = int(connection.scalar(text("SHOW server_version_num")) or 0)
            if not 170000 <= version < 180000:
                return False
            revisions = connection.scalars(
                text("SELECT version_num FROM control_api.alembic_version")
            ).all()
            if revisions != [SCHEMA_REVISION]:
                return False
            contract = connection.scalar(
                text("SELECT contract FROM control_api.foundation_metadata WHERE singleton = true")
            )
            return bool(contract == SCHEMA_CONTRACT)

    def close(self) -> None:
        self.engine.dispose()

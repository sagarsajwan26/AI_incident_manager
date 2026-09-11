from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class IntegrationProvider(str, Enum):
    GITHUB = "github"
    SLACK = "slack"


class Integration(Base):
    __tablename__ = "Integrations"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "provider",
            name="uq_integration_tenant_provider",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id"),
        nullable=False,
    )

    provider: Mapped[IntegrationProvider] = mapped_column(
        SQLEnum(IntegrationProvider),
        nullable=False,
    )

    credentials: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class PolicyType(str, enum.Enum):
    LOGICAL = "LOGICAL"
    NATURAL_LANGUAGE = "NATURAL_LANGUAGE"


class PolicyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    policy_type: Mapped[PolicyType] = mapped_column(
        Enum(PolicyType), default=PolicyType.NATURAL_LANGUAGE, nullable=False
    )
    natural_language: Mapped[str | None] = mapped_column(Text, nullable=True)
    dsl: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus), default=PolicyStatus.DRAFT, nullable=False
    )
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    created_by: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

"""Issue database model."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import Category, Status, TargetType


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False, index=True
    )
    room_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("rooms.id"), nullable=True, index=True
    )
    target_type: Mapped[TargetType] = mapped_column(
        Enum(TargetType, native_enum=False, create_constraint=True, name="target_type"),
        nullable=False,
        index=True,
    )
    target: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[Category] = mapped_column(
        Enum(Category, native_enum=False, create_constraint=True, name="category"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[Status] = mapped_column(
        Enum(Status, native_enum=False, create_constraint=True, name="status"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    updated_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="issues")
    room: Mapped["Room | None"] = relationship(back_populates="issues")
    creator: Mapped["User"] = relationship(
        back_populates="created_issues", foreign_keys=[created_by]
    )
    updater: Mapped["User"] = relationship(
        back_populates="updated_issues", foreign_keys=[updated_by]
    )
    comments: Mapped[list["Comment"]] = relationship(back_populates="issue")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="issue")

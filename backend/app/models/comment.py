"""Comment database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    issue_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("issues.id"), nullable=False, index=True
    )
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    issue: Mapped["Issue"] = relationship(back_populates="comments")
    creator: Mapped["User"] = relationship(back_populates="comments")

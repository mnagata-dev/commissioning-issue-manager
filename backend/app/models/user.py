from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.enums import Role


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum(Role, native_enum=False, create_constraint=True, name="role"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    created_issues: Mapped[list["Issue"]] = relationship(
        back_populates="creator", foreign_keys="Issue.created_by"
    )
    updated_issues: Mapped[list["Issue"]] = relationship(
        back_populates="updater", foreign_keys="Issue.updated_by"
    )
    comments: Mapped[list["Comment"]] = relationship(back_populates="creator")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="uploader")

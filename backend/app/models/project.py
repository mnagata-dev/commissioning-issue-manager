from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    hotel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hotels.id"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    hotel: Mapped["Hotel"] = relationship(back_populates="projects")
    issues: Mapped[list["Issue"]] = relationship(back_populates="project")

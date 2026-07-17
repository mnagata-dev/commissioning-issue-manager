from datetime import datetime

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.orm import relationship

from app.db.base import Base


class Hotel(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    projects: Mapped[list["Project"]] = relationship(back_populates="hotel")
    room_types: Mapped[list["RoomType"]] = relationship(back_populates="hotel")
    rooms: Mapped[list["Room"]] = relationship(back_populates="hotel")

"""Room database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (
        UniqueConstraint(
            "hotel_id", "room_number", name="uq_rooms_hotel_id_room_number"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("hotels.id"), nullable=False, index=True
    )
    room_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("room_types.id"), nullable=False
    )
    room_number: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    hotel: Mapped["Hotel"] = relationship(back_populates="rooms")
    room_type: Mapped["RoomType"] = relationship(back_populates="rooms")
    issues: Mapped[list["Issue"]] = relationship(back_populates="room")

"""Event model for special game events."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.game import Game


class EventType(str, enum.Enum):
    """Special event type enumeration."""
    
    INQUISITOR = "inquisitor"           # Sheriff can see all roles
    MAYOR_ELECTION = "mayor_election"   # Elect a mayor
    PLAGUE = "plague"                   # Random player loses ability
    FULL_MOON = "full_moon"             # Maniac can kill 2 people
    CURFEW = "curfew"                   # No talking during day
    DOUBLE_TROUBLE = "double_trouble"   # Two mafia kills
    REVELATION = "revelation"           # Random role is revealed
    NONE = "none"


class Event(Base):
    """Special event model."""
    
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    # Foreign Key
    game_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("games.id"),
        nullable=False,
    )
    
    # Event details
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Effect tracking
    affected_player_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    effect_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="events")
    
    def __repr__(self) -> str:
        return f"<Event(game={self.game_id}, type={self.event_type}, day={self.day_number})>"
    
    def complete(self) -> None:
        """Mark event as completed."""
        self.is_completed = True
        self.ended_at = datetime.utcnow()
    
    @property
    def is_ongoing(self) -> bool:
        """Check if event is still ongoing."""
        return self.is_active and not self.is_completed

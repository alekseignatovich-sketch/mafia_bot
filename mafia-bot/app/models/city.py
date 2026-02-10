"""City model."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.game import Game


class City(Base):
    """City model representing a game instance."""
    
    __tablename__ = "cities"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_players: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    min_players: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    
    # Creator
    creator_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        nullable=False,
    )
    
    # Game Settings
    day_duration_hours: Mapped[int] = mapped_column(Integer, default=16, nullable=False)
    night_duration_hours: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    players: Mapped[List["Player"]] = relationship(
        "Player",
        secondary="city_players",
        back_populates="cities",
        lazy="selectin",
    )
    games: Mapped[List["Game"]] = relationship(
        "Game",
        back_populates="city",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<City(id={self.id}, name={self.name}, players={len(self.players)})>"
    
    @property
    def player_count(self) -> int:
        """Get current player count."""
        return len(self.players)
    
    @property
    def is_full(self) -> bool:
        """Check if city is full."""
        return self.player_count >= self.max_players
    
    @property
    def can_start(self) -> bool:
        """Check if game can start."""
        return self.player_count >= self.min_players


# Association table for City-Player many-to-many relationship
class CityPlayer(Base):
    """Association table for city players."""
    
    __tablename__ = "city_players"
    
    city_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("cities.id"),
        primary_key=True,
    )
    player_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        primary_key=True,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

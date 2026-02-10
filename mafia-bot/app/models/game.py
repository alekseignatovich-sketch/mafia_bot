"""Game model."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.city import City
    from app.models.player import Player
    from app.models.role import PlayerRole
    from app.models.action import Action
    from app.models.vote import Vote
    from app.models.event import Event


class GameStatus(str, enum.Enum):
    """Game status enumeration."""
    
    WAITING = "waiting"          # Waiting for players
    STARTING = "starting"        # Countdown to start
    NIGHT = "night"              # Night phase
    DAY = "day"                  # Day phase
    VOTING = "voting"            # Voting phase
    ENDED = "ended"              # Game ended
    PAUSED = "paused"            # Game paused


class Game(Base):
    """Game model representing a single game session."""
    
    __tablename__ = "games"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    city_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("cities.id"),
        nullable=False,
    )
    
    # Game Status
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus),
        default=GameStatus.WAITING,
        nullable=False,
    )
    
    # Phase tracking
    day_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    phase_end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Winner
    winner_faction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    city: Mapped["City"] = relationship("City", back_populates="games")
    players: Mapped[List["Player"]] = relationship(
        "Player",
        secondary="game_players",
        back_populates="games",
        lazy="selectin",
    )
    roles: Mapped[List["PlayerRole"]] = relationship(
        "PlayerRole",
        back_populates="game",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    actions: Mapped[List["Action"]] = relationship(
        "Action",
        back_populates="game",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    votes: Mapped[List["Vote"]] = relationship(
        "Vote",
        back_populates="game",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="game",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Game(id={self.id}, city={self.city_id}, status={self.status}, day={self.day_number})>"
    
    @property
    def alive_players(self) -> List["PlayerRole"]:
        """Get all alive players."""
        return [r for r in self.roles if r.is_alive]
    
    @property
    def alive_mafia(self) -> List["PlayerRole"]:
        """Get alive mafia players."""
        from app.models.role import RoleType
        return [
            r for r in self.roles 
            if r.is_alive and r.role.role_type == RoleType.MAFIA
        ]
    
    @property
    def alive_civilians(self) -> List["PlayerRole"]:
        """Get alive civilian players."""
        from app.models.role import RoleType
        return [
            r for r in self.roles 
            if r.is_alive and r.role.role_type == RoleType.CIVILIAN
        ]
    
    @property
    def is_night(self) -> bool:
        """Check if it's night phase."""
        return self.status == GameStatus.NIGHT
    
    @property
    def is_day(self) -> bool:
        """Check if it's day phase."""
        return self.status in [GameStatus.DAY, GameStatus.VOTING]


# Association table for Game-Player many-to-many relationship
class GamePlayer(Base):
    """Association table for game players."""
    
    __tablename__ = "game_players"
    
    game_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("games.id"),
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

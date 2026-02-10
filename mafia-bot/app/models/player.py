"""Player model."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.achievement import PlayerAchievement
    from app.models.city import City
    from app.models.game import Game
    from app.models.role import PlayerRole


class Player(Base):
    """Player model representing a Telegram user."""
    
    __tablename__ = "players"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Game Progress
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reputation: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Settings
    language: Mapped[str] = mapped_column(String(5), default="ru", nullable=False)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Statistics
    games_played: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    games_won: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    games_lost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_days_survived: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    
    # Relationships
    cities: Mapped[List["City"]] = relationship(
        "City",
        secondary="city_players",
        back_populates="players",
        lazy="selectin",
    )
    games: Mapped[List["Game"]] = relationship(
        "Game",
        secondary="game_players",
        back_populates="players",
        lazy="selectin",
    )
    roles: Mapped[List["PlayerRole"]] = relationship(
        "PlayerRole",
        foreign_keys="[PlayerRole.player_id]",  # ← КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ
        back_populates="player",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    achievements: Mapped[List["PlayerAchievement"]] = relationship(
        "PlayerAchievement",
        back_populates="player",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Player(id={self.id}, telegram_id={self.telegram_id}, name={self.first_name})>"
    
    @property
    def display_name(self) -> str:
        """Get player display name."""
        if self.username:
            return f"@{self.username}"
        return self.first_name
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100
    
    def add_experience(self, amount: int) -> bool:
        """Add experience and check for level up."""
        from app.config import settings
        
        self.experience += amount
        required_xp = self.level * settings.XP_LEVEL_MULTIPLIER
        
        if self.experience >= required_xp:
            self.level += 1
            self.experience -= required_xp
            return True
        return False

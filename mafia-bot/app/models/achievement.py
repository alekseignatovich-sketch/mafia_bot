"""Achievement model."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.player import Player


class Achievement(Base):
    """Achievement template model."""
    
    __tablename__ = "achievements"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    description_key: Mapped[str] = mapped_column(String(128), nullable=False)
    
    # Icon/Emoji
    icon: Mapped[str] = mapped_column(String(8), default="🏆", nullable=False)
    
    # Requirements
    requirement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    requirement_value: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Reward
    xp_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    player_achievements: Mapped[List["PlayerAchievement"]] = relationship(
        "PlayerAchievement",
        back_populates="achievement",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Achievement(id={self.id}, name={self.name})>"


class PlayerAchievement(Base):
    """Player's earned achievement."""
    
    __tablename__ = "player_achievements"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    # Foreign Keys
    player_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        nullable=False,
    )
    achievement_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("achievements.id"),
        nullable=False,
    )
    
    # Progress
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    earned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="player_achievements")
    
    def __repr__(self) -> str:
        return f"<PlayerAchievement(player={self.player_id}, achievement={self.achievement_id})>"
    
    def complete(self) -> None:
        """Mark achievement as completed."""
        self.is_completed = True
        self.earned_at = datetime.utcnow()
        self.progress = self.achievement.requirement_value

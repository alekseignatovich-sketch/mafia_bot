"""Action model for night actions."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, BigInteger, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.role import PlayerRole


class ActionType(str, enum.Enum):
    """Action type enumeration."""
    
    # Mafia
    KILL = "kill"
    
    # Doctor
    HEAL = "heal"
    
    # Sheriff
    INVESTIGATE = "investigate"
    
    # Maniac
    MANIAC_KILL = "maniac_kill"
    
    # Cupid
    MATCHMAKE = "matchmake"
    
    # Prostitute/Hooker
    BLOCK = "block"
    
    # Bodyguard
    PROTECT = "protect"
    
    # Special
    NONE = "none"


class Action(Base):
    """Night action model."""
    
    __tablename__ = "actions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    # Foreign Keys
    game_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("games.id"),
        nullable=False,
    )
    player_role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("player_roles.id"),
        nullable=False,
    )
    target_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("player_roles.id"),
        nullable=True,
    )
    
    # Action details
    action_type: Mapped[ActionType] = mapped_column(Enum(ActionType), nullable=False)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Result
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="actions")
    player_role: Mapped["PlayerRole"] = relationship(
        "PlayerRole",
        foreign_keys=[player_role_id],
        back_populates="actions",
    )
    target: Mapped[Optional["PlayerRole"]] = relationship(
        "PlayerRole",
        foreign_keys=[target_id],
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Action(game={self.game_id}, type={self.action_type}, day={self.day_number})>"
    
    def mark_processed(self, success: bool, result: str) -> None:
        """Mark action as processed."""
        self.success = success
        self.result = result
        self.processed_at = datetime.utcnow()

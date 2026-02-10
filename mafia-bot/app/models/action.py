"""Action model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.role import PlayerRole


class ActionType(str):
    """Action type constants."""
    KILL = "kill"
    HEAL = "heal"
    INVESTIGATE = "investigate"
    PROTECT = "protect"


class Action(Base):
    __tablename__ = "actions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    # Кто совершил действие
    actor_role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("player_roles.id"),
        nullable=False,
    )
    
    # На кого направлено (опционально)
    target_role_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("player_roles.id"),
        nullable=True,
    )
    
    action_type: Mapped[str] = mapped_column(String(32), nullable=False)
    game_night: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    
    # Связи
    actor_role: Mapped["PlayerRole"] = relationship(
        "PlayerRole",
        foreign_keys=[actor_role_id],
        back_populates="actions"
    )
    
    target_role: Mapped[Optional["PlayerRole"]] = relationship(
        "PlayerRole",
        foreign_keys=[target_role_id],
        back_populates="received_actions"  # ← если нужно
    )
    
    def __repr__(self) -> str:
        return f"<Action(id={self.id}, type={self.action_type}, night={self.game_night})>"

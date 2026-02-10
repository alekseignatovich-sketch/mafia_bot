"""Action model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.role import PlayerRole


# ✅ ДОБАВЛЕНО: ActionType как Enum
class ActionType(str):
    """Action type constants."""
    KILL = "kill"
    HEAL = "heal"
    INVESTIGATE = "investigate"
    PROTECT = "protect"
    BLOCK = "block"
    REVEAL = "reveal"


class Action(Base):
    """Represents an in-game action (kill, heal, investigate, etc.)."""
    
    __tablename__ = "actions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    # 🔗 Обязательная связь с игрой
    game_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("games.id"),
        nullable=False,
    )
    
    # Исполнитель действия (роль игрока)
    actor_role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("player_roles.id"),
        nullable=False,
    )
    
    # Цель действия (опционально)
    target_role_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("player_roles.id"),
        nullable=True,
    )
    
    # Тип действия — теперь можно использовать ActionType.KILL и т.д.
    action_type: Mapped[str] = mapped_column(String(32), nullable=False)
    
    # Ночь, в которую совершено действие
    game_night: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Время создания
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    
    # 🔁 Связи
    game: Mapped["Game"] = relationship("Game", back_populates="actions")
    
    actor_role: Mapped["PlayerRole"] = relationship(
        "PlayerRole",
        foreign_keys=[actor_role_id],
        back_populates="actions"
    )
    
    target_role: Mapped[Optional["PlayerRole"]] = relationship(
        "PlayerRole",
        foreign_keys=[target_role_id],
        back_populates="received_actions"
    )
    
    def __repr__(self) -> str:
        return f"<Action(id={self.id}, type={self.action_type}, night={self.game_night})>"

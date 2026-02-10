"""Role model."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.game import Game
    from app.models.action import Action


class RoleType(str, enum.Enum):
    """Role type enumeration."""
    
    CIVILIAN = "civilian"
    MAFIA = "mafia"
    NEUTRAL = "neutral"


class Role(Base):
    """Role template model."""
    
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    name_key: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    description_key: Mapped[str] = mapped_column(String(64), nullable=False)
    
    # Role properties
    role_type: Mapped[RoleType] = mapped_column(Enum(RoleType), nullable=False)
    team: Mapped[str] = mapped_column(String(32), nullable=False)  # mafia, town, neutral
    
    # Abilities
    can_kill: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_heal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_investigate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_block: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Priority (lower = earlier in night)
    action_priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    # Unlocked at level
    unlock_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Is special role (for events)
    is_special: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    player_roles: Mapped[List["PlayerRole"]] = relationship(
        "PlayerRole",
        back_populates="role",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name}, type={self.role_type})>"


class PlayerRole(Base):
    """Player's role in a specific game."""
    
    __tablename__ = "player_roles"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    # Foreign Keys
    player_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        nullable=False,
    )
    game_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("games.id"),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("roles.id"),
        nullable=False,
    )
    
    # Status
    is_alive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_revealed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Special status
    is_mayor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_lover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    lover_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        nullable=True,
    )
    
    # Ability cooldowns
    ability_cooldown: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Death info
    died_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    death_cause: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    
    # Relationships
    player: Mapped["Player"] = relationship(
        "Player",
        foreign_keys=[player_id],
        back_populates="roles"
    )
    
    # Опционально: связь с "любовником" (если используется)
    # lover: Mapped[Optional["Player"]] = relationship(
    #     "Player",
    #     foreign_keys=[lover_id],
    #     back_populates="lovers"  # ← требует добавления в Player
    # )
    
    game: Mapped["Game"] = relationship("Game", back_populates="roles")
    role: Mapped["Role"] = relationship("Role", back_populates="player_roles")
    
    # Связь с действиями, где ЭТОТ PlayerRole — исполнитель
    actions: Mapped[List["Action"]] = relationship(
        "Action",
        foreign_keys="[Action.actor_role_id]",
        back_populates="actor_role",
        lazy="selectin",
    )
    
    # Опционально: связь с действиями, где ЭТОТ PlayerRole — цель
    # received_actions: Mapped[List["Action"]] = relationship(
    #     "Action",
    #     foreign_keys="[Action.target_role_id]",
    #     back_populates="target_role",
    #     lazy="selectin",
    # )
    
    def __repr__(self) -> str:
        return f"<PlayerRole(player={self.player_id}, role={self.role_id}, alive={self.is_alive})>"
    
    @property
    def faction(self) -> str:
        """Get player's faction."""
        return self.role.team
    
    @property
    def can_use_ability(self) -> bool:
        """Check if player can use their ability."""
        return self.is_alive and self.ability_cooldown == 0
    
    def kill(self, cause: str) -> None:
        """Kill the player."""
        self.is_alive = False
        self.died_at = datetime.utcnow()
        self.death_cause = cause

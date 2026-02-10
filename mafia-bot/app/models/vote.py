"""Vote model for day voting."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, BigInteger, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.role import PlayerRole


class Vote(Base):
    """Vote model for day voting phase."""
    
    __tablename__ = "votes"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    # Foreign Keys
    game_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("games.id"),
        nullable=False,
    )
    voter_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("player_roles.id"),
        nullable=False,
    )
    target_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("player_roles.id"),
        nullable=False,
    )
    
    # Vote details
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # Mayor has 2 votes
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="votes")
    voter: Mapped["PlayerRole"] = relationship(
        "PlayerRole",
        foreign_keys=[voter_id],
        lazy="selectin",
    )
    target: Mapped["PlayerRole"] = relationship(
        "PlayerRole",
        foreign_keys=[target_id],
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Vote(game={self.game_id}, voter={self.voter_id}, target={self.target_id})>"
    
    def revoke(self) -> None:
        """Revoke the vote."""
        self.is_active = False
        self.revoked_at = datetime.utcnow()

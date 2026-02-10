"""Role manager service."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role, RoleType


class RoleManager:
    """Manager for game roles."""
    
    # Default roles configuration
    DEFAULT_ROLES = [
        {
            "name": "Civilian",
            "name_key": "civilian",
            "description_key": "roles.civilian.description",
            "role_type": RoleType.CIVILIAN,
            "team": "town",
            "action_priority": 10,
            "unlock_level": 1,
        },
        {
            "name": "Mafia",
            "name_key": "mafia",
            "description_key": "roles.mafia.description",
            "role_type": RoleType.MAFIA,
            "team": "mafia",
            "can_kill": True,
            "action_priority": 3,
            "unlock_level": 1,
        },
        {
            "name": "Doctor",
            "name_key": "doctor",
            "description_key": "roles.doctor.description",
            "role_type": RoleType.CIVILIAN,
            "team": "town",
            "can_heal": True,
            "action_priority": 4,
            "unlock_level": 2,
        },
        {
            "name": "Sheriff",
            "name_key": "sheriff",
            "description_key": "roles.sheriff.description",
            "role_type": RoleType.CIVILIAN,
            "team": "town",
            "can_investigate": True,
            "action_priority": 5,
            "unlock_level": 3,
        },
        {
            "name": "Maniac",
            "name_key": "maniac",
            "description_key": "roles.maniac.description",
            "role_type": RoleType.NEUTRAL,
            "team": "neutral",
            "can_kill": True,
            "action_priority": 1,
            "unlock_level": 5,
        },
        {
            "name": "Cupid",
            "name_key": "cupid",
            "description_key": "roles.cupid.description",
            "role_type": RoleType.CIVILIAN,
            "team": "town",
            "action_priority": 2,
            "unlock_level": 4,
        },
        {
            "name": "Prostitute",
            "name_key": "prostitute",
            "description_key": "roles.prostitute.description",
            "role_type": RoleType.CIVILIAN,
            "team": "town",
            "can_block": True,
            "action_priority": 2,
            "unlock_level": 3,
        },
        {
            "name": "Bodyguard",
            "name_key": "bodyguard",
            "description_key": "roles.bodyguard.description",
            "role_type": RoleType.CIVILIAN,
            "team": "town",
            "action_priority": 1,
            "unlock_level": 4,
        },
        {
            "name": "Don",
            "name_key": "don",
            "description_key": "roles.don.description",
            "role_type": RoleType.MAFIA,
            "team": "mafia",
            "can_kill": True,
            "can_investigate": True,
            "action_priority": 3,
            "unlock_level": 5,
        },
    ]
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def initialize_default_roles(self) -> None:
        """Initialize default roles in database."""
        for role_data in self.DEFAULT_ROLES:
            # Check if role already exists
            result = await self.session.execute(
                select(Role).where(Role.name_key == role_data["name_key"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                role = Role(**role_data)
                self.session.add(role)
        
        await self.session.commit()
    
    async def get_available_roles(self, player_level: int = 1) -> List[Role]:
        """Get roles available for player's level."""
        result = await self.session.execute(
            select(Role)
            .where(Role.unlock_level <= player_level)
            .where(Role.is_special == False)
        )
        return result.scalars().all()
    
    async def get_role_by_key(self, key: str) -> Optional[Role]:
        """Get role by name key."""
        result = await self.session.execute(
            select(Role).where(Role.name_key == key)
        )
        return result.scalar_one_or_none()
    
    async def get_roles_by_type(self, role_type: RoleType) -> List[Role]:
        """Get all roles of specific type."""
        result = await self.session.execute(
            select(Role).where(Role.role_type == role_type)
        )
        return result.scalars().all()

"""XP and level manager service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.achievement import Achievement, PlayerAchievement
from app.models.player import Player


class XPManager:
    """Manager for player experience and levels."""
    
    # Achievement definitions
    ACHIEVEMENTS = [
        {
            "name": "First Blood",
            "name_key": "first_blood",
            "description_key": "achievements.first_blood.description",
            "icon": "🩸",
            "requirement_type": "night_kills",
            "requirement_value": 1,
            "xp_reward": 10,
        },
        {
            "name": "Savior",
            "name_key": "savior",
            "description_key": "achievements.savior.description",
            "icon": "💉",
            "requirement_type": "heals",
            "requirement_value": 10,
            "xp_reward": 25,
        },
        {
            "name": "Detective",
            "name_key": "detective",
            "description_key": "achievements.detective.description",
            "icon": "🔍",
            "requirement_type": "correct_investigations",
            "requirement_value": 5,
            "xp_reward": 30,
        },
        {
            "name": "Survivor",
            "name_key": "survivor",
            "description_key": "achievements.survivor.description",
            "icon": "🛡️",
            "requirement_type": "nights_survived_single_game",
            "requirement_value": 10,
            "xp_reward": 50,
        },
        {
            "name": "Legend",
            "name_key": "legend",
            "description_key": "achievements.legend.description",
            "icon": "👑",
            "requirement_type": "level_reached",
            "requirement_value": 10,
            "xp_reward": 100,
        },
    ]
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def initialize_achievements(self) -> None:
        """Initialize default achievements."""
        for ach_data in self.ACHIEVEMENTS:
            from sqlalchemy import select
            result = await self.session.execute(
                select(Achievement).where(Achievement.name_key == ach_data["name_key"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                achievement = Achievement(**ach_data)
                self.session.add(achievement)
        
        await self.session.commit()
    
    async def add_xp(self, player: Player, amount: int) -> bool:
        """Add XP to player and check for level up.
        
        Returns:
            True if player leveled up
        """
        leveled_up = player.add_experience(amount)
        await self.session.commit()
        
        # Check for level-based achievements
        if leveled_up:
            await self.check_achievement(player, "level_reached", player.level)
        
        return leveled_up
    
    async def check_achievement(self, player: Player, requirement_type: str, value: int) -> None:
        """Check and award achievements."""
        from sqlalchemy import select
        
        # Get achievements of this type
        result = await self.session.execute(
            select(Achievement).where(Achievement.requirement_type == requirement_type)
        )
        achievements = result.scalars().all()
        
        for achievement in achievements:
            # Check if player already has this achievement
            result = await self.session.execute(
                select(PlayerAchievement).where(
                    PlayerAchievement.player_id == player.id,
                    PlayerAchievement.achievement_id == achievement.id,
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                if not existing.is_completed:
                    # Update progress
                    existing.progress = value
                    if value >= achievement.requirement_value:
                        existing.complete()
                        # Award XP
                        await self.add_xp(player, achievement.xp_reward)
            else:
                # Create new player achievement
                player_ach = PlayerAchievement(
                    player_id=player.id,
                    achievement_id=achievement.id,
                    progress=value,
                    is_completed=value >= achievement.requirement_value,
                )
                self.session.add(player_ach)
                
                if player_ach.is_completed:
                    # Award XP
                    await self.add_xp(player, achievement.xp_reward)
        
        await self.session.commit()
    
    def get_required_xp(self, level: int) -> int:
        """Get XP required for level."""
        return level * settings.XP_LEVEL_MULTIPLIER
    
    def get_level_title(self, level: int) -> str:
        """Get title for level."""
        titles = {
            (1, 2): "Новичок 🌱",
            (3, 4): "Опытный игрок 🌿",
            (5, 6): "Мастер игры 🌳",
            (7, 8): "Эксперт 🏆",
            (9, 10): "Легенда 👑",
        }
        
        for (min_lvl, max_lvl), title in titles.items():
            if min_lvl <= level <= max_lvl:
                return title
        
        return "Бог игры 🌟"

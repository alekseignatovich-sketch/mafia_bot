"""Game engine service."""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.action import Action, ActionType
from app.models.game import Game, GameStatus
from app.models.player import Player
from app.models.role import PlayerRole, RoleType
from app.models.vote import Vote


class GameEngine:
    """Game engine for processing game phases."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def start_night(self, game: Game) -> None:
        """Start night phase."""
        game.status = GameStatus.NIGHT
        game.phase_end_time = datetime.utcnow() + timedelta(
            hours=settings.NIGHT_START_HOUR + 24 - settings.DAY_START_HOUR
        )
        
        await self.session.commit()
    
    async def end_night(self, game: Game) -> None:
        """End night phase and process actions."""
        # Get all actions for this night
        actions = await self.session.execute(
            select(Action)
            .where(Action.game_id == game.id)
            .where(Action.day_number == game.day_number)
            .where(Action.processed_at.is_(None))
            .order_by(Action.created_at)
        )
        actions = actions.scalars().all()
        
        # Process actions by priority
        await self._process_night_actions(game, actions)
        
        # Check win conditions
        winner = await self._check_win_conditions(game)
        if winner:
            await self._end_game(game, winner)
            return
        
        # Start day phase
        await self.start_day(game)
    
    async def _process_night_actions(self, game: Game, actions: List[Action]) -> None:
        """Process all night actions in priority order."""
        # Track protected and healed players
        protected_players = set()
        healed_players = set()
        killed_players = set()
        
        # Sort actions by role priority
        sorted_actions = sorted(
            actions,
            key=lambda a: a.player_role.role.action_priority
        )
        
        for action in sorted_actions:
            if not action.player_role.is_alive:
                continue
            
            if action.action_type == ActionType.PROTECT:
                # Bodyguard protection
                if action.target:
                    protected_players.add(action.target.player_id)
                    action.mark_processed(True, f"Protected {action.target.player.display_name}")
            
            elif action.action_type == ActionType.HEAL:
                # Doctor heal
                if action.target:
                    healed_players.add(action.target.player_id)
                    action.mark_processed(True, f"Healed {action.target.player.display_name}")
            
            elif action.action_type == ActionType.BLOCK:
                # Prostitute block
                if action.target:
                    # Block target's action for this night
                    action.mark_processed(True, f"Blocked {action.target.player.display_name}")
            
            elif action.action_type == ActionType.INVESTIGATE:
                # Sheriff investigation
                if action.target:
                    is_mafia = action.target.role.role_type == RoleType.MAFIA
                    result = "is_mafia" if is_mafia else "not_mafia"
                    action.mark_processed(True, result)
            
            elif action.action_type in [ActionType.KILL, ActionType.MANIAC_KILL]:
                # Mafia or Maniac kill
                if action.target:
                    target_id = action.target.player_id
                    
                    # Check if target is protected or healed
                    if target_id in protected_players or target_id in healed_players:
                        action.mark_processed(False, "Target was protected")
                    else:
                        killed_players.add(target_id)
                        action.mark_processed(True, f"Killed {action.target.player.display_name}")
        
        # Apply deaths
        for action in sorted_actions:
            if action.action_type in [ActionType.KILL, ActionType.MANIAC_KILL]:
                if action.target and action.target.player_id in killed_players:
                    action.target.kill("killed_night")
        
        await self.session.commit()
    
    async def start_day(self, game: Game) -> None:
        """Start day phase."""
        game.status = GameStatus.DAY
        game.day_number += 1
        game.phase_end_time = datetime.utcnow() + timedelta(
            hours=settings.DAY_START_HOUR + 16
        )
        
        await self.session.commit()
    
    async def start_voting(self, game: Game) -> None:
        """Start voting phase."""
        game.status = GameStatus.VOTING
        await self.session.commit()
    
    async def process_votes(self, game: Game) -> Optional[PlayerRole]:
        """Process votes and return executed player or None."""
        # Get active votes for current day
        votes = await self.session.execute(
            select(Vote)
            .where(Vote.game_id == game.id)
            .where(Vote.day_number == game.day_number)
            .where(Vote.is_active == True)
        )
        votes = votes.scalars().all()
        
        if not votes:
            return None
        
        # Count votes
        vote_counts = {}
        for vote in votes:
            target_id = vote.target_id
            vote_counts[target_id] = vote_counts.get(target_id, 0) + vote.weight
        
        # Find player with most votes
        max_votes = max(vote_counts.values())
        alive_count = len(game.alive_players)
        
        # Need majority to execute
        if max_votes > alive_count / 2:
            executed_id = max(vote_counts, key=vote_counts.get)
            
            result = await self.session.execute(
                select(PlayerRole).where(PlayerRole.id == executed_id)
            )
            executed = result.scalar_one_or_none()
            
            if executed:
                executed.kill("executed")
                await self.session.commit()
                return executed
        
        return None
    
    async def _check_win_conditions(self, game: Game) -> Optional[str]:
        """Check if game has a winner.
        
        Returns:
            Winner faction or None if game continues
        """
        alive_mafia = len(game.alive_mafia)
        alive_civilians = len(game.alive_civilians)
        
        # Mafia wins if they equal or outnumber civilians
        if alive_mafia >= alive_civilians:
            return "mafia"
        
        # Civilians win if no mafia left
        if alive_mafia == 0:
            return "town"
        
        return None
    
    async def _end_game(self, game: Game, winner: str) -> None:
        """End the game."""
        game.status = GameStatus.ENDED
        game.winner_faction = winner
        game.ended_at = datetime.utcnow()
        
        # Update player statistics
        for player_role in game.roles:
            player = player_role.player
            player.games_played += 1
            
            if player_role.faction == winner:
                player.games_won += 1
            else:
                player.games_lost += 1
            
            # Add XP
            xp_gain = settings.XP_PER_CYCLE * game.day_number
            if player_role.faction == winner:
                xp_gain *= 2  # Bonus for winning
            
            player.add_experience(xp_gain)
        
        await self.session.commit()

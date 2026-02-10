"""Tests for database models."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player
from app.models.city import City
from app.models.game import Game, GameStatus


@pytest.mark.asyncio
async def test_player_creation(session: AsyncSession):
    """Test player creation."""
    player = Player(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User",
        language="ru",
    )
    session.add(player)
    await session.commit()
    
    assert player.id is not None
    assert player.telegram_id == 123456789
    assert player.display_name == "@testuser"


@pytest.mark.asyncio
async def test_city_creation(session: AsyncSession):
    """Test city creation."""
    # Create player first
    player = Player(
        telegram_id=123456789,
        first_name="Test",
    )
    session.add(player)
    await session.flush()
    
    city = City(
        name="Test City",
        description="A test city",
        creator_id=player.id,
    )
    session.add(city)
    await session.commit()
    
    assert city.id is not None
    assert city.name == "Test City"
    assert city.creator_id == player.id


@pytest.mark.asyncio
async def test_game_creation(session: AsyncSession):
    """Test game creation."""
    # Create player and city
    player = Player(
        telegram_id=123456789,
        first_name="Test",
    )
    session.add(player)
    await session.flush()
    
    city = City(
        name="Test City",
        creator_id=player.id,
    )
    session.add(city)
    await session.flush()
    
    game = Game(
        city_id=city.id,
        status=GameStatus.WAITING,
    )
    session.add(game)
    await session.commit()
    
    assert game.id is not None
    assert game.status == GameStatus.WAITING
    assert game.city_id == city.id


@pytest.mark.asyncio
async def test_player_experience(session: AsyncSession):
    """Test player experience and leveling."""
    player = Player(
        telegram_id=123456789,
        first_name="Test",
        level=1,
        experience=0,
    )
    session.add(player)
    await session.commit()
    
    # Add experience
    leveled_up = player.add_experience(5)
    await session.commit()
    
    assert player.experience == 5
    assert not leveled_up
    
    # Add more experience to level up
    leveled_up = player.add_experience(10)
    await session.commit()
    
    assert player.level == 2
    assert leveled_up

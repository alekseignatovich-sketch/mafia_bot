# ER Диаграмма базы данных

```mermaid
erDiagram
    PLAYER ||--o{ CITY_PLAYERS : joins
    CITY ||--o{ CITY_PLAYERS : has
    PLAYER ||--o{ GAME_PLAYERS : plays
    GAME ||--o{ GAME_PLAYERS : includes
    CITY ||--o{ GAME : hosts
    PLAYER ||--o{ PLAYER_ROLE : has
    GAME ||--o{ PLAYER_ROLE : assigns
    ROLE ||--o{ PLAYER_ROLE : defines
    GAME ||--o{ ACTION : contains
    PLAYER_ROLE ||--o{ ACTION : performs
    GAME ||--o{ VOTE : has
    PLAYER_ROLE ||--o{ VOTE : casts
    PLAYER_ROLE ||--o{ VOTE : receives
    GAME ||--o{ EVENT : triggers
    PLAYER ||--o{ PLAYER_ACHIEVEMENT : earns
    ACHIEVEMENT ||--o{ PLAYER_ACHIEVEMENT : defines

    PLAYER {
        bigint id PK
        bigint telegram_id UK
        string username
        string first_name
        string last_name
        int level
        int experience
        int reputation
        boolean is_active
        boolean is_banned
        string language
        boolean notifications_enabled
        int games_played
        int games_won
        int games_lost
        int total_days_survived
        datetime last_activity
        datetime registered_at
        datetime created_at
        datetime updated_at
    }

    CITY {
        bigint id PK
        string name
        text description
        boolean is_active
        boolean is_private
        int max_players
        int min_players
        bigint creator_id FK
        int day_duration_hours
        int night_duration_hours
        datetime created_at
        datetime ended_at
        datetime created_at
        datetime updated_at
    }

    CITY_PLAYERS {
        bigint city_id PK,FK
        bigint player_id PK,FK
        datetime joined_at
    }

    GAME {
        bigint id PK
        bigint city_id FK
        enum status
        int day_number
        datetime phase_end_time
        string winner_faction
        datetime started_at
        datetime ended_at
        datetime created_at
        datetime updated_at
    }

    GAME_PLAYERS {
        bigint game_id PK,FK
        bigint player_id PK,FK
        datetime joined_at
    }

    ROLE {
        bigint id PK
        string name
        string name_key UK
        string description_key
        enum role_type
        string team
        boolean can_kill
        boolean can_heal
        boolean can_investigate
        boolean can_block
        int action_priority
        int unlock_level
        boolean is_special
        datetime created_at
        datetime updated_at
    }

    PLAYER_ROLE {
        bigint id PK
        bigint player_id FK
        bigint game_id FK
        bigint role_id FK
        boolean is_alive
        boolean is_revealed
        boolean is_mayor
        boolean is_lover
        bigint lover_id FK
        int ability_cooldown
        datetime died_at
        string death_cause
        datetime created_at
        datetime updated_at
    }

    ACTION {
        bigint id PK
        bigint game_id FK
        bigint player_role_id FK
        bigint target_id FK
        enum action_type
        int day_number
        text result
        boolean success
        datetime created_at
        datetime processed_at
    }

    VOTE {
        bigint id PK
        bigint game_id FK
        bigint voter_id FK
        bigint target_id FK
        int day_number
        int weight
        boolean is_active
        datetime created_at
        datetime revoked_at
    }

    EVENT {
        bigint id PK
        bigint game_id FK
        enum event_type
        int day_number
        text description
        boolean is_active
        boolean is_completed
        bigint affected_player_id
        text effect_data
        datetime started_at
        datetime ended_at
        datetime created_at
        datetime updated_at
    }

    ACHIEVEMENT {
        bigint id PK
        string name
        string name_key UK
        string description_key
        string icon
        string requirement_type
        int requirement_value
        int xp_reward
        datetime created_at
        datetime updated_at
    }

    PLAYER_ACHIEVEMENT {
        bigint id PK
        bigint player_id FK
        bigint achievement_id FK
        int progress
        boolean is_completed
        datetime earned_at
        datetime created_at
        datetime updated_at
    }
```

## Описание связей

### Player (Игрок)
- **CITY_PLAYERS** (Many-to-Many): Игрок может присоединяться к нескольким городам
- **GAME_PLAYERS** (Many-to-Many): Игрок может участвовать в нескольких играх
- **PLAYER_ROLE** (One-to-Many): Игрок может иметь разные роли в разных играх
- **PLAYER_ACHIEVEMENT** (One-to-Many): Игрок может заработать множество достижений

### City (Город)
- **CITY_PLAYERS** (Many-to-Many): Город имеет множество игроков
- **GAME** (One-to-Many): В городе может быть множество игр
- **PLAYER** (Many-to-One): Город создан одним игроком

### Game (Игра)
- **GAME_PLAYERS** (Many-to-Many): Игра включает множество игроков
- **PLAYER_ROLE** (One-to-Many): В игре назначаются роли игрокам
- **ACTION** (One-to-Many): В игре выполняются ночные действия
- **VOTE** (One-to-Many): В игре проводятся голосования
- **EVENT** (One-to-Many): В игре могут происходить спецсобытия

### Role (Роль)
- **PLAYER_ROLE** (One-to-Many): Шаблон роли используется для назначения игрокам

### PlayerRole (Роль игрока в игре)
- **ACTION** (One-to-Many): Игрок с ролью выполняет действия
- **VOTE** (One-to-Many as voter): Игрок голосует
- **VOTE** (One-to-Many as target): За игрока голосуют

### Achievement (Достижение)
- **PLAYER_ACHIEVEMENT** (One-to-Many): Шаблон достижения зарабатывается игроками

# Руководство по развертыванию

## Содержание
- [Локальное развертывание](#локальное-развертывание)
- [Docker развертывание](#docker-развертывание)
- [Render.com](#rendercom)
- [Hetzner/VPS](#hetznervps)
- [Настройка webhook](#настройка-webhook)

## Локальное развертывание

### Требования
- Python 3.10+
- PostgreSQL 14+
- Git

### Шаги

1. **Клонирование репозитория**
```bash
git clone https://github.com/yourusername/mafia-bot.git
cd mafia-bot
```

2. **Создание виртуального окружения**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка базы данных PostgreSQL**
```bash
# Создание базы данных
sudo -u postgres createdb mafia_bot

# Создание пользователя (опционально)
sudo -u postgres createuser -P mafia_user
```

5. **Настройка переменных окружения**
```bash
cp .env.example .env
nano .env  # Редактирование
```

6. **Запуск миграций**
```bash
alembic upgrade head
```

7. **Запуск бота**
```bash
python bot.py
```

## Docker развертывание

### Требования
- Docker
- Docker Compose

### Шаги

1. **Настройка переменных окружения**
```bash
cp .env.example .env
nano .env
```

2. **Запуск**
```bash
docker-compose up -d
```

3. **Просмотр логов**
```bash
docker-compose logs -f bot
```

4. **Остановка**
```bash
docker-compose down
```

## Render.com

### Шаги

1. Создайте аккаунт на [Render.com](https://render.com)

2. Создайте новый Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`

3. Добавьте переменные окружения:
   - `BOT_TOKEN`
   - `DATABASE_URL`
   - `ADMIN_IDS`

4. Добавьте PostgreSQL базу данных:
   - New → PostgreSQL
   - Скопируйте Internal Database URL в `DATABASE_URL`

5. Deploy!

## Hetzner/VPS

### Шаги

1. **Создание сервера**
   - Рекомендуется: CX21 (2 vCPU, 4 GB RAM)
   - OS: Ubuntu 22.04 LTS

2. **Подключение и настройка**
```bash
ssh root@your-server-ip

# Обновление системы
apt update && apt upgrade -y

# Установка зависимостей
apt install -y python3-pip python3-venv postgresql redis-server git

# Настройка PostgreSQL
sudo -u postgres createdb mafia_bot
sudo -u postgres createuser -P mafia_user

# Клонирование
mkdir -p /opt/mafia-bot
cd /opt/mafia-bot
git clone https://github.com/yourusername/mafia-bot.git .

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настройка .env
nano .env

# Миграции
alembic upgrade head
```

3. **Создание systemd сервиса**
```bash
nano /etc/systemd/system/mafia-bot.service
```

```ini
[Unit]
Description=Mafia Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/mafia-bot
Environment=PATH=/opt/mafia-bot/venv/bin
ExecStart=/opt/mafia-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable mafia-bot
systemctl start mafia-bot

# Просмотр статуса
systemctl status mafia-bot

# Просмотр логов
journalctl -u mafia-bot -f
```

## Настройка Webhook

### Требования
- Домен с HTTPS
- SSL сертификат

### Настройка

1. **Добавьте в .env:**
```env
WEBHOOK_HOST=https://your-domain.com
WEBHOOK_PATH=/webhook
```

2. **Настройка Nginx**
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /webhook {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Перезапуск**
```bash
systemctl restart nginx
systemctl restart mafia-bot
```

## Мониторинг

### Логи
```bash
# Docker
docker-compose logs -f bot

# Systemd
journalctl -u mafia-bot -f

# Файл
 tail -f logs/bot.log
```

### Метрики
```bash
# Просмотр активных игр
psql -U mafia_user -d mafia_bot -c "SELECT COUNT(*) FROM games WHERE status != 'ended';"

# Просмотр игроков
psql -U mafia_user -d mafia_bot -c "SELECT COUNT(*) FROM players;"
```

## Резервное копирование

### База данных
```bash
# Создание бэкапа
pg_dump -U mafia_user mafia_bot > backup_$(date +%Y%m%d).sql

# Восстановление
psql -U mafia_user -d mafia_bot < backup_20240115.sql
```

### Автоматическое резервное копирование
```bash
# Добавьте в crontab
crontab -e

# Ежедневный бэкап в 3:00
0 3 * * * pg_dump -U mafia_user mafia_bot > /backups/mafia_bot_$(date +\%Y\%m\%d).sql
```

## Устранение неполадок

### Бот не запускается
```bash
# Проверка логов
journalctl -u mafia-bot -n 50

# Проверка переменных окружения
cat /opt/mafia-bot/.env

# Проверка подключения к БД
psql $DATABASE_URL -c "SELECT 1;"
```

### Ошибки базы данных
```bash
# Пересоздание таблиц
alembic downgrade base
alembic upgrade head

# Или полный сброс
dropdb mafia_bot
createdb mafia_bot
alembic upgrade head
```

### Проблемы с webhook
```bash
# Проверка SSL
openssl s_client -connect your-domain.com:443

# Проверка webhook
curl -X POST https://your-domain.com/webhook -d '{}'
```

# WebSocket Chat
---

## Technology Stack:
- FastAPI
- WebSocket
- Uvicorn (server)
- Postgres
- SQLAlchemy
- Alembic
- Celery
- Aiogram
- Pytest
- Docker, docker compose
- Fabric (deploy)
- SSL Certificate with Let's Encrypt

## How to start the app?
### Local Environment
```bash
git clone git@github.com:sannjka/chat.git
cd chat
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
uvicorn src.main:app --port=8010 --reload
```
We are going to need the `.env` file:
```
SECRET_KEY=your-secret-key
ALGORITHM=HS256
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
TG_TOKEN=your-telegram-bot-token
CELERY_BROKER=pyamqp://localhost:5672//
```
Also we need:  
- database with the name that corresponds this `.env` settings
- `rabbitmq` or another broker set up

Run telegram bot (used to subscribe for notification about missed messages):
```bash
python tg_bot.py
```

Run celery worker:
```bash
celery -A celery_worker worker --loglevel=INFO
```

visit url: localhost:8010

### Local Environment (Docker)
```bash
git clone git@github.com:sannjka/chat.git
cd chat
docker compose -f local_docker-compose.yml up -d --build
```
`.env` file:
```
SECRET_KEY=your-secret-key
ALGORITHM=HS256
DB_HOST=db
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-db-password
TG_TOKEN=your-telegram-bot-token
CELERY_BROKER=pyamqp://localhost:5672//
```
`.env-postgres` file:
```
POSTGRES_PASSWORD=your-db-password
```
visit url: localhost:8011

### Server
For server Ubuntu with Nginx and Docker  
On local computer do:
```bash
git clone git@github.com:sannjka/chat.git
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cd chat/deploy_tools
```
In `nginx.template.conf` correct path to ssl certificate
If you do not have a certificate, delete all that marked as `# managed by Certbot`
```bash
fab -H user_on_server@server_name deploy
```

## Features
- WebSocket chat for authorized users
- There are common and private chats
- Messages from private chats are saved in db
- Logged out users may receive notifications in telegram. To subscribe to notifications send a telegram message to th bot with the email of your chat user

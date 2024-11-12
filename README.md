# WebSocket Chat
---

## Technology Stack:
- FastAPI
- WebSocket
- Uvicorn (server)
- Postgres
- SQLAlchemy
- Alembic
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
visit url: localhost:8010

### Local Environment (Docker)
```bash
git clone git@github.com:sannjka/chat.git
cd chat
docker compose -f local_docker-compose.yml up -d --build
```
visit url: localhost:8011

### Server
For server Ubuntu with Nginx and Docker  
On local computer do:
```bash
git clone git@github.com:sannjka/chat.git
cd chat/deploy_tools
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
```
In `nginx.template.conf` correct path to ssl certificate
If you do not have a certificate, delete all that marked as `# managed by Certbot`
```bash
fab -H user_on_server@server_name deploy
```

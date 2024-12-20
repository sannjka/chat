FROM python:3.11-alpine

WORKDIR /home/chat

COPY requirements requirements
RUN pip install --upgrade pip && pip install -r requirements/docker.txt

COPY migration migration
COPY src src
COPY alembic.ini ./
COPY boot.sh ./
RUN chmod 755 boot.sh
COPY celery_worker.py tg_bot.py ./

# runtime configuration
EXPOSE 8011
#ENTRYPOINT ["./boot.sh"]

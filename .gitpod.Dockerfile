FROM gitpod/workspace-postgres

RUN sudo apt-get update \
    && sudo apt-get install -y p7zip-full \
    && sudo apt-get install -y rabbitmq-server \
    && sudo apt-get install -y redis-server \
    && pip install --upgrade pip \
    && pip install pipenv \
    && pip install supervisor \
    && sudo rm -rf /var/lib/apt/lists/*
ENV DATABASE_URL psql://gitpod@127.0.0.1:5432/adit
ENV DJANGO_SETTINGS_MODULE adit.settings.development

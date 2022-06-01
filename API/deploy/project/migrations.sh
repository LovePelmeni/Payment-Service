#!/bin/sh

echo "Running Migrations.."
cd ./API

alembic init migrations
echo "Migrated... Editing Configuration."
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi

python ./deploy/project/replace_default_config.py
echo "Configuration Replaced.. Testing..."
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi

alembic revision --autogenerate -m "Make Migrations..."
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi

echo "Migrating..."
alembic upgrade head
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi
echo "Migrated Successfully."




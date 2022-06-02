#!/bin/sh

DIR="API/migrations/"
echo "Running Migrations.."
cd ./API

alembic init migrations
echo "Migrated... Editing Configuration."
if [$? -ne 0]; then
echo "Failed to Make Init Migration Directory. Seems Like Its Exists. Exiting..."

if [-d "$DIR"]; then

    python ./deploy/project/replace_default_config.py
    if [$? -ne 0]; then
    echo "Could not replace configuration. Exiting..."
    exit 1;
    fi
    echo "Configuration Replaced.. Testing..."
fi


    alembic revision --autogenerate -m "Make Migrations..."
      if [$? -ne 0]; then
      echo "Failed to make migrations. Exiting..."
      exit 1;
      fi

    echo "Migrating..."
    alembic upgrade head
    if [$? -ne 0]; then
    echo "Failed to Start Celery Beat Worker. Exiting..."
    exit 1;
    fi
    echo "Migrated Successfully."

fi
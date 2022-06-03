#!/bin/sh

ln -s /Users/kirillklimushin/PycharmProjects/FastAPIPaymentProject/API ~/API
ln -s /Users/kirillklimushin/PycharmProjects/FastAPIPaymentProject/API/migrations/ ~/migrations

CONFIG_REPLACE_EXECUTOR_DIR=~/deploy/project/replace_default_config.py
WORKDIR=~/API
MIGRATIONS_DIR=~/migrations
echo "Running Migrations.."



cd "$WORKDIR"

if [-d "$MIGRATIONS_DIR"]; then
    echo "Directory  Migrations already exists. Skipping...."
else
  alembic init migrations
  echo "Made Initial Migrations Directory Editing Configuration."
  if [$? -ne 0]; then
  echo "Failed to Make Init Migration Directory. Seems Like Its Exists. Exiting..."
  fi

  python "$CONFIG_REPLACE_EXECUTOR_DIR"
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


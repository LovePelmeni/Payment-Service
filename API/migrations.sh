#!/bin/sh

alembic revision --autogenerate -m "Migrations"
if [$? -ne 0]; then
  echo "Failed to make migrations. Exiting..."
  exit 1;
fi

echo "Migrating..."
alembic upgrade head
if [$? -ne 0]; then
echo "Migration Failed."
exit 1;
fi
echo "Migrated Successfully."





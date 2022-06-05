#!/bin/sh

INTEGRATION_TESTS_DIR=./tests/test_integrations.py
MODULE_TESTS_DIR=./tests/test_modules.py
MIGRATION_SHELL_FILE=./migrations.sh

cd ./API
sh "$MIGRATION_SHELL_FILE"

echo "Running Services Integration Tests..."
pytest "$INTEGRATION_TESTS_DIR"
if [$? -ne 0]; then
echo "Failed to run integration tests. Exiting..."
exit 1;
fi
echo "Run Successfully."

echo "Running Module Tests..."
pytest -q "$MODULE_TESTS_DIR"
if [$? -ne 0]; then
echo "Failed to run module tests. Exiting..."
exit 1;
fi
echo "Run Successfully."

cd -
echo "Starting Fast API Application..."
uvicorn API.settings:application --host 0.0.0.0 --port 8081
if [$? -ne 0]; then
echo "Failed to Fast API Application. Exiting..."
exit 1;
fi



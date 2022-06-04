#!/bin/sh

INTEGRATION_TESTS_DIR=./tests/integration_tests.py
MODULE_TESTS_DIR=./tests/module_tests.py
STRIPE_API_SECRET=${STRIPE_API_SECRET}

docker run -v /var/run/docker.sock:/var/run/docker.sock --privileged \
stripe/stripe-cli listen --api-key "$STRIPE_API_SECRET" \
--forward-to http://localhost:8081/webhook/payment/ \
--events, payment_intent.succeeded,payment_intent.failed \

echo "Running Migrations Shell Script..."
sh ./migrations.sh
echo "Migrations Shell Script has run successfully."

echo "Running Services Integration Tests..."
pytest -q "$INTEGRATION_TESTS_DIR"
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi
echo "Run Successfully."

echo "Running Module Tests..."
pytest -q "$MODULE_TESTS_DIR"
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi
echo "Run Successfully."

pwd
echo "Starting Fast API Application..."
uvicorn settings:application --host 0.0.0.0 --port 8081
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi


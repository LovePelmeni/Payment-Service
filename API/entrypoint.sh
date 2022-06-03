#!/bin/sh

INTEGRATION_TESTS_DIR=./tests/integration_tests.py
MODULE_TESTS_DIR=./tests/module_tests.py

echo "Running Migrations Shell Script..."
sh chmod +x ./migrations.sh
sh ./migrations.sh
echo "Migrations Shell Script has run successfully."

echo "Running Services Integration Tests..."
python pytest -q "$INTEGRATION_TESTS_DIR"
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi
echo "Run Successfully."

echo "Running Module Tests..."
python pytest -q "$MODULE_TESTS_DIR"
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi
echo "Run Successfully."

echo "Starting Fast API Application..."
uvicorn API.settings:application --host 0.0.0.0 --port 8081 &
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi

echo "Logging to Stripe API."
stripe login --api-key ${STRIPE_API_KEY} &

if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi

echo "starting Payment Webhook Service.."
stripe listen --forward-to 0.0.0.0:8081/webhook/payment/ --events payment_intent.succeeded payment_intent.failed &
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi
echo "Testing Webhook..."
stripe trigger payment_intent.succeeded
if [$? -ne 0]; then
echo "Webhook Responded with Exception. Exiting..."
exit 1;
fi
echo "Webhook Is Configured."
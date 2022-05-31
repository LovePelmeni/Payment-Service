#!/bin/sh
echo "Running Test Webhook Endpoint.."
stripe login --api-key ${STRIPE_API_KEY}
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi

stripe --forward-to ${TEST_SERVER_HOST}:${TEST_SERVER_PORT}/payment/webhook/ &
echo "Stripe Webhook Listener is running."
if [$? -ne 0]; then
echo "Failed to Start Celery Beat Worker. Exiting..."
exit 1;
fi

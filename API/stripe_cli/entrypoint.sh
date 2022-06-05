#!/bin/sh
echo "Starting Stripe CLI."
cd "$(dirname "$0")"
python ./stripe_cli.py
echo "started.."
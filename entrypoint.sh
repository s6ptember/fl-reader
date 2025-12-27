#!/bin/bash
set -e

echo "Starting Tor service..."
tor -f /etc/tor/torrc &
TOR_PID=$!

echo "Waiting for Tor to establish connection..."
sleep 10

if ! kill -0 $TOR_PID 2>/dev/null; then
    echo "ERROR: Tor failed to start"
    exit 1
fi

echo "Tor is running (PID: $TOR_PID)"

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

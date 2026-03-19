#!/bin/bash

# streamYourClaw startup script

echo "Starting streamYourClaw..."

# Check if Redis is running
if ! docker ps | grep -q redis; then
    echo "Starting Redis container..."
    docker run -d --name streamyourclaw-redis -p 6379:6379 redis:alpine
fi

# Wait for Redis to be ready
echo "Waiting for Redis..."
sleep 2

# Start the backend server
echo "Starting backend server..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
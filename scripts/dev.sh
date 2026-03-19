#!/bin/bash

# streamYourClaw development startup script

echo "Starting streamYourClaw in development mode..."

# Start Redis if not running
if ! docker ps | grep -q redis; then
    echo "Starting Redis container..."
    docker run -d --name streamyourclaw-redis -p 6379:6379 redis:alpine
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env from example..."
    cp .env.example .env
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -e ".[dev]"
else
    source venv/bin/activate
fi

# Start backend
echo "Starting backend server..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
#!/usr/bin/env python3
"""Start Redis server using redislite with TCP port."""

import redislite
import time
import os
import redis

# Create Redis instance in user's home directory
redis_path = os.path.expanduser("~/.streamyourclaw/redis.db")
os.makedirs(os.path.dirname(redis_path), exist_ok=True)

print(f"Starting Redis server at {redis_path}...")

# Use TCP port 6379
redis_server = redislite.Redis(redis_path, port=6379)

# Wait for Redis to be ready
time.sleep(3)

# Test connection using standard redis client
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    if r.ping():
        print("✓ Redis server is running on port 6379!")
        print("  Connection: redis://localhost:6379/0")
        print("\nRedis is ready.")
    else:
        print("✗ Redis ping failed")
except Exception as e:
    print(f"✗ Error: {e}")

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY backend/requirements.txt ./backend/
COPY backend/app ./backend/app/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend
COPY frontend ./frontend

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FRONTEND_PATH=/app/frontend

# Run the application
WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
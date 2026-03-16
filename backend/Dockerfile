FROM python:3.11-slim

WORKDIR /app

# No system deps needed: psycopg2-binary and asyncpg use pre-built wheels

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (__pycache__ excluded via .dockerignore)
COPY . .

# Run database migrations and start server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

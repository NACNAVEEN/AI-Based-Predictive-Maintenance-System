# Dockerfile for Predictive Maintenance API
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies (slim version needs compiler tools for lightgbm/xgboost if wheel is not available)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY api/ ./api/
COPY database/ ./database/
COPY models/ ./models/

# Expose the API port
EXPOSE 8000

# Run uvicorn to start the API
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT}

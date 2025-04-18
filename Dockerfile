FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY api_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r api_requirements.txt

# Copy application code
COPY api_server.py .
COPY update_urls.py .
COPY .env* .

# Expose API port
EXPOSE 8000

# Command to run the application
CMD ["python", "api_server.py"] 
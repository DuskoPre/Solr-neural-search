FROM python:3.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY scripts/ ./scripts/
COPY data/ ./data/

# Make scripts executable
RUN chmod +x scripts/*.py

CMD ["python", "-c", "print('Neural Search App Ready! Use docker exec to run scripts.')"]

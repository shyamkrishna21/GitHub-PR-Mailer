# Use base image
FROM python:3.11-slim

# Set environment variables 
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory 
WORKDIR /app

# Copy the requirements 
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
       cron \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install -r requirements.txt \
    && apt-get purge -y --auto-remove gcc \
    && apt-get clean \
    && rm -rf /root/.cache

# Copy the rest of the application code
COPY . .

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

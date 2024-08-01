# Base image
FROM python:3.11-slim AS base

# Builder image
FROM base AS builder

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
       cron \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements
COPY requirements.txt .

# Create virtual environment and install Python packages
RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

# Runner image
FROM base AS runner

# Install only runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev \
       cron \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy python dependencies
COPY --from=builder /venv /venv

# Copy code
COPY . /app

# Ensure that the virtual environment is used
ENV PATH="/venv/bin:$PATH"

# Entrypoint script executable
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]


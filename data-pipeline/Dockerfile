FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install seqkit
ARG SEQKIT_VERSION=2.8.2
RUN wget -q https://github.com/shenwei356/seqkit/releases/download/v${SEQKIT_VERSION}/seqkit_linux_amd64.tar.gz \
    && tar -xzf seqkit_linux_amd64.tar.gz \
    && mv seqkit /usr/local/bin/ \
    && rm seqkit_linux_amd64.tar.gz \
    && seqkit version

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY src/ ./src/
COPY samples/ ./samples/
COPY tests/ ./tests/

# Expose Dagster webserver port
EXPOSE 3000

# Set environment variables
ENV DAGSTER_HOME=/app
ENV PATH="/app/.venv/bin:$PATH"

# Run Dagster webserver
CMD ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]

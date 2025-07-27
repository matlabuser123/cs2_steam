# Multi-stage build for CS2 optimization toolkit
FROM nvidia/cuda:11.8.0-base-ubuntu22.04 as base

# Set working directory
WORKDIR /app

# Install system dependencies with optimizations
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    unzip wine wget curl git \
    build-essential \
    nvidia-utils-535 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.11 /usr/bin/python

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better Docker layer caching
COPY requirements.txt ./
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install project in development mode
RUN pip install -e .

# Set environment variables
ENV PYTHONPATH=/app
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd -m -u 1000 cs2user && \
    chown -R cs2user:cs2user /app
USER cs2user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default entrypoint
ENTRYPOINT ["python"]
CMD ["main.py"]

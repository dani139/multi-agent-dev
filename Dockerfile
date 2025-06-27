FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    unzip \
    software-properties-common \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI for agent container management
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for web development capabilities
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install Python dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium firefox webkit

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/temp

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash multiagent \
    && chown -R multiagent:multiagent /app \
    && chown -R multiagent:multiagent /opt/venv

# Switch to non-root user
USER multiagent

# Expose ports
EXPOSE 8080 8501 8502 9090

# Set default command
CMD ["python", "main.py"] 
# Stage 1: Build dependencies with Nix
FROM nixos/nix AS builder

# Copy project files
COPY . /app
WORKDIR /app

# Install Nix dependencies
RUN nix-env -iA nixpkgs.poetry
RUN poetry install --no-dev

# Stage 2: Runtime image
FROM python:3.9-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Nix
RUN curl -L https://nixos.org/nix/install | sh

# Copy built dependencies from builder stage
COPY --from=builder /app /app
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/root/.nix-profile/bin:${PATH}"

# Install Python dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Expose port for potential web service
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["python", "bluefin_trader.py"]
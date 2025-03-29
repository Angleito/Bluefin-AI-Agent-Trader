FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY ./requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY ./services/chart /app

# Create directories
RUN mkdir -p /app/logs /app/screenshots

# Set user for better security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose the service port
EXPOSE 3333

# Run the service
CMD ["python", "app.py"] 
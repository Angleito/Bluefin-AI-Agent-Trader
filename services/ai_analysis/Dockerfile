FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY ./services/ai_analysis /app

# Create logs directory
RUN mkdir -p /app/logs

# Set user for better security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose the service port
EXPOSE 5000

# Run the service
CMD ["python", "app.py"] 
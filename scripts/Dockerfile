FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create logs directory
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Expose port
EXPOSE 5000

# Declare volume for persistent logs
VOLUME ["/app/logs"]

# Set environment variables
ENV FLASK_APP=app.py
ENV LOG_FILE=/app/logs/access.log

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
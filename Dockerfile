FROM python:3.10-slim

# Install system dependencies (includes what's needed for psycopg2 + your listed ones)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev libmagic1 dnsutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Daphne and Celery
RUN pip install daphne celery

# Copy the application code into the container
COPY . .

# Set environment variables
ENV REDIS_SSL_CERT_REQS=none

# Expose the port for the application
EXPOSE 8000

# Copy and prepare entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["gunicorn", "umemployed.wsgi:application", "--bind", "0.0.0.0:$PORT"]

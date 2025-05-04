FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y libmagic1 dnsutils

# Set work directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Set environment variables (for Django and Redis configuration, modify as needed)
ENV REDIS_SSL_CERT_REQS=none

# Run Django migrations (to ensure the database is ready)
RUN python manage.py migrate --noinput

# Collect static files (necessary for production environments)
RUN python manage.py collectstatic --noinput

# Expose the port for the application (8000 for Django development)
EXPOSE 8000

# Add entrypoint script to manage application startup and migration
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command (can be overridden)
CMD ["gunicorn", "umemployed.wsgi:application", "--bind", "0.0.0.0:8000"]

FROM python:3.10

# Install dependencies
RUN apt-get update && apt-get install -y libmagic1 dnsutils

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Set environment variables
ENV REDIS_SSL_CERT_REQS=none

# Collect static files
RUN python manage.py collectstatic --no-input

# Add entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
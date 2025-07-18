# Use a lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONUNBUFFERED=1

# Install system dependencies for MySQL and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --timeout 600

# Copy the entire project
COPY . .

# Collect static files (Google Cloud Run does not persist them)
RUN python manage.py collectstatic --noinput

# Expose port 8080 (Cloud Run expects this)
EXPOSE 8080

# Use Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "multi_store_pos.wsgi:application"]

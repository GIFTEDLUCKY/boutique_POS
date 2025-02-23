FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files
ENV VAR=value

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    --fix-missing \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt --timeout 600

# Copy the rest of your application code into the container
COPY . /app/

# Expose port (assuming the app will run on port 8000)
EXPOSE 8000

# Run the application (assume it's using the default Django runserver command)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Use official Python 3.13 slim image as base
FROM python:3.13-slim

# Set environment variables for Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Avoid Python buffering for logs
ENV PYTHONUNBUFFERED=1

# Install system dependencies and OpenJDK 17
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk git curl && \
    rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy project files to container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Render (use the port your app runs on)
EXPOSE 10000

# Start the Flask app with gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:10000"]

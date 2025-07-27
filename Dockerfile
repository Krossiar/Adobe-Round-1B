# Use Python base image
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Set environment variables to reduce startup time
ENV TRANSFORMERS_CACHE=/app/cache

# Create output directory
RUN mkdir -p /app/output

# Run script
CMD ["python", "main.py"]

FROM python:3.11-slim

WORKDIR /app

# Copy frontend files
COPY . .

# Install Python (for http.server)
RUN pip install --no-cache-dir flask

# Start server
CMD ["python3", "-m", "http.server", "8000", "--bind", "0.0.0.0"]
